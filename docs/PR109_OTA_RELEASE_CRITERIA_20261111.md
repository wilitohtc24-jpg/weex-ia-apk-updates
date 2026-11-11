# WEEX IA Trader — siguiente OTA (PR108 + PR109), 11 nov 2026

Estado: **NO PUBLICAR**. El usuario pidió una única próxima APK por OTA (desde la app), **solo cuando funcione correctamente**. La APK instalada que abre es la recuperación manual **v29333175**, procedente de `manual-pr106-v29333175`, con un VerifyError histórico ya reparado parcialmente. El catálogo OTA oficial `releases/latest` sigue publicando `v29176085`; NO retroceder.

## Identidad de lanzamiento innegociable
- Package: `com.wilito.weexautotrader`
- Certificado Android original SHA-256: `5d0698ff9d09d7928944d01260d30b277ca4d20bd52c6cc583147b436b6c22e6`.
- Nueva `versionCode > 29333175`, incluso cuando `releases/latest` sea inferior; comparar contra la **instalada**, no solo contra la última OTA.
- GitHub OTA: `wilitohtc24-jpg/weex-ia-apk-updates`, ruta GitHub Releases **latest, non-prerelease, non-draft**, asset `WEEX-IA-Trader-release.apk`; la versión de prueba manual en prerelease no la detecta el actualizador.
- SHA-256 real en binario, firma v2, `aapt dump badging`, release.json canónico y build-source SHA exactos. Firmar con el certificado histórico original; nunca publicar DEBUG o clave desechable.

## Estado del código
- Recuperación PR #106 de `TraderService` pasó DEX classload ART e instalación sobre versión anterior en teléfono, pero hubo bloqueos de Samsung y ciclos WAIT lentos.
- PR #108 (base `repair/pr102-art-verifyerror-20261110`): modifica exclusivamente la comprobación final de ajuste de STOP propio, conserva el selector REAL; materialización Kotlin/JUnit **PASS** run `42961183300`, emulador Android ART **PASS** run `42962533048`. **No demuestra todavía stops WEEX verificados ni funcionamiento continuado en móvil**.
- PR #109 (base PR108, rama `repair/weex-dynamic-spread-20261111`): corregir la discrepancia entre filtro duro spread 0.15% y microestructura 0.25%, solo si TP esperable cubre costes. Requiere pasar íntegra la última ejecución de Kotlin/JUnit; NO declarar PASS solo por gate de fuente.
- Riesgo 8% individual y 12% agregado todavía vigentes; propuesta 20% es **estudio**, no está activa. No afirmar corregido el sizing ni prometer beneficio fijo.
- Issues #104 (protección ganancias), #107 (selector/WAIT/Samsung), #105 (VerifyError pasado) continúan documentando los síntomas.

## Evidencia adicional de las seis capturas REAL (11 nov, 12:22–12:26)
- Escáner 72→78→84→90→96→108 /197, sí avanza de seis en seis, aún falta probar vuelta completa y recuperación.
- LPT SHORT: R/R 0.24R <1.55R; CVX SHORT: contrafactual TP-first 24%, SL-first 49%, n67/14 independientes; MORPHO LONG: no hay geometría ejecutable LATERAL; XVG SHORT: RR neto 1.03R <1.20R, costes 0.364%; MEGA SHORT: contrafactual TP-first 21%, SL-first 63%, n67/14 independientes. No eliminar puertas sin demostrar señales válidas y positivo SIM/REAL.
- **COMP SHORT: BLOQUEANTE DE ENTREGA** issue #110: HTTP 400 WEEX -1141 = PARAM_EMPTY (campo obligatorio ausente) en solicitud de apalancamiento. Revisar GET symbolConfig, ruta POST confirmada y mensaje sanitizado con pruebas offline de LONG/SHORT. No se debe pasar a orden sin confirmación de leverage; resolver sin alterar manuales.
- Issue #107 tiene análisis completo y condiciones de aceptación. PR #109 superó suite final Kotlin/JUnit run 42965200814, pero no valida por sí solo este problema ni arranque/gestión REAL.

## Nueva prueba concluyente — apalancamiento REAL `-1141` (WXDG2-77873f7b0619)

- 11-nov-2026 06:15:41 UTC, versión instalada `29333175` (MANTA-USDT SHORT 4h, 90 puntos, cobertura 192/197); `weexNetwork.status` registra exactamente el campo que faltó: `Parameter 'isolatedLongLeverage' cannot be empty.` No orden REAL enviada; API de saldo y ledger frescos.
- La referencia oficial de WEEX V3 documenta una sola dirección como suficiente, pero el servidor para este caso exigió ambas. Las correcciones deben basarse en la **respuesta real**. https://www.weex.com/api-doc/contract/Account_API/UpdateLeverageTRADE
- **P0 antes de OTA:** PR #111 DRAFT en rama `repair/weex-1141-dual-field-preserve-20261111`, encima de #109, prepara ambos campos conservando el apalancamiento contrario del `symbolConfig` firmado. Nunca inventar 20x contrario; exigir modo ISOLATED/COMBINED, sin posición del símbolo, estabilidad de doble GET y confirmación posterior de ambos valores. El POST 200 no equivale a autorización de orden. No usar live WEEX en CI.
- CI de solo Kotlin/JUnit PR #111 **PASS confirmado** el 11-nov-2026 a las 06:27 UTC: https://github.com/wilitohtc24-jpg/weex-ia-apk-updates/actions/runs/42972012184. El log verifica `WEEX_PRESIGN_SOURCE_GATES_PASSED_NO_APK_NO_OTA_NO_ORDERS`, `PR111_SIGNED_LEVERAGE_DUAL_SIDE_FINAL_SOURCE_PRESENT` y `PR111_ANDROID_KOTLIN_JUNIT_PASS_NO_APK_NO_OTA_NO_ORDERS`. **No equivale a prueba de arranque ART de la combinación PR111 ni integración WEEX simulada.**
- Otro hallazgo: `runtime.cycleMs=12279`, `traderCycleStalled=false`, `scannerAlignedWithTrading=true`, así que este WAIT no fue un congelamiento. `readiness=16%` y `profitFactor=0.12` son telemetría de preparación, no prueba causal de este error; `positions=0` impide validar ratchet SL.
- Neon `httpStatus=413` al guardar respaldo es una incidencia separada; tratar lotes y compresión de copia sin perder datos, no condicionar nuevas entradas válidas al resultado del respaldo.
- Las capturas del usuario muestran `197/197` en SAHARA seguido de `6/197` en ZEC y `12/197` AVAX: evidencia de al menos una vuelta completa con reinicio de contador; no demuestra libre de bloqueos/ANR sostenidos.

## ART de la combinación PR111 — PASS limitado (11-nov-2026, 09:49 UTC)

- Run [42996874254](https://github.com/wilitohtc24-jpg/weex-ia-apk-updates/actions/runs/42996874254) **SUCCESS**: fuente final de PR111 commit `2836b8e0d2c3c7228cbb4751f18f22a778632249` fijada; materialización canónica y Kotlin/JUnit PASS; compilación DEBUG temporal; instrumentación Android ART verificó carga/continuación del worker `TraderService` sin `VerifyError` y sin crash en esa prueba. No se publicó ni firmó APK de distribución.
- **Alcance estricto:** el propio workflow declara `no app launch`; esto es un test de carga ART del worker, **NO** una prueba de arranque completo de la app ni de 10 ciclos SIM/REAL. Tampoco prueba modificación remota de SL/TP, instalación `adb install -r` con datos persistentes, certificado histórico ni `versionCode` final. Mantener **NO PUBLICAR**.
- Último run del workflow específico PR109 `weex-pr109-dynamic-spread-kotlin-junit-20261111.yml`: [42965200814](https://github.com/wilitohtc24-jpg/weex-ia-apk-updates/actions/runs/42965200814) PASS a las 05:27 UTC. PR108/109/111 siguen DRAFT. Issues #104/#105/#107 siguen OPEN. Ningún fallo nuevo de esta ejecución exige parche adicional.

## QA PR #111 confirmada y pendiente (11-nov, mañana)

- **PASS fuente materializada + Kotlin/JUnit**: https://github.com/wilitohtc24-jpg/weex-ia-apk-updates/actions/runs/42972012184. **PASS carga DEX de TraderService por Android ART**, usando APK debug descartable: https://github.com/wilitohtc24-jpg/weex-ia-apk-updates/actions/runs/42996874254. Ambos verificaron exactamente commit `2836b8e0d2c3c7228cbb4751f18f22a778632249` del PR #111, no una release firmada.
- **Prueba adicional offline LauncherActivity → MainActivity y reinstalación con datos**: https://github.com/wilitohtc24-jpg/weex-ia-apk-updates/actions/runs/43035837520. Requiere resultado SUCCESS. Usa solo emulador vacío, sin conexión, credenciales ni órdenes y firma DEBUG descartable; **no sustituye** a `adb install -r` de la APK release firmada sobre un build real anterior.
- **Fallo potencial descubierto revisando código del SL ratchet**, issue #104: `modifyTpSlOrder` puede resultar efectivo remotamente y la lectura `openConditionalOrders` posterior puede fallar. Queda SL local antiguo; en siguientes ciclos la búsqueda por SL viejo no reconoce el nuevo y puede bloquear indefinidamente la gestión. Requiere ensayo de fallo de GET tras POST, reinicio y recuperación duradera por mismo `algoId`, sin segunda modificación ciega ni intervención sobre posiciones manuales. No afirmar protección de ganancias REAL verificada mientras esté pendiente.
- El monitor de próxima OTA ahora consulta PR #108/#109/#111, issue #110, pruebas Android y este documento. **No publicar una APK** hasta completar la verificación de riesgos, firma y actualizador.

## PR #112 — recuperación durable de SL y dos gestores (11 nov 2026)

- DRAFT https://github.com/wilitohtc24-jpg/weex-auto-trader-android/pull/112; rama `repair/weex-ratchet-pending-reconcile-20261111`, basada en PR #111. Guarda `positionId, symbol, side, algoId, oldStop, newStop` en journal durable antes de `modifyTpSlOrder`; recupera el STOP remoto por mismo algoId/estado/trigger antes de actualizar el SL local. Si GET falla, el resultado queda incierto y NO se reenvía el POST. Preserva origen firmado, cierres prioritarios y stops manuales.
- La primera ejecución `43038447702` falló porque `modern_peak_profit_protection_proof_v1.py` exigía la secuencia antigua exacta de lectura después de POST. Se reforzó ese verificador con una rama exclusivamente para el diario durable, exigiendo nuevo journal/orden de operaciones sin relajar casos antiguos. Repetición: https://github.com/wilitohtc24-jpg/weex-ia-apk-updates/actions/runs/43039117348; NO marcar PASS sin conclusión exitosa.
- BLOQUEANTE REAL: la materialización también añade `RealAdaptiveStopManager.maybeProtect` en `RealAIExitEngine`, que puede enviar su propio `modifyTpSlOrder` sin compartir el diario del gestor principal. Issue #104 documenta coordinación requerida: un único escritor o mutex/journal compartido para ambos, pruebas de concurrencia y reinicio. PR112 por sí solo no garantiza ratchet REAL totalmente conciliado.
- Otra prueba Android offline de la fuente PR111: https://github.com/wilitohtc24-jpg/weex-ia-apk-updates/actions/runs/43038549096. La primera ejecución `43035837520` falló solo porque el ejecutor corrió tres métodos pero esperaba uno. Se corrigió el selector a un método exacto; la nueva prueba aún debe confirmar launcher, persistencia y reinstalación.

## PR113 — diario único para los DOS gestores de SL REAL

- DRAFT `https://github.com/wilitohtc24-jpg/weex-auto-trader-android/pull/113`: basado en PR112, añade mutex por proceso a `RealStopAmendmentJournal.begin/clearAfterReconciliation` y obliga a `RealAdaptiveStopManager` a registrar intent en el **mismo diario** antes de `modifyTpSlOrder`, abstenerse ante pending de otro gestor y exigir readback firmado exacto por algoId/símbolo/lado/SL. Así no pueden reemitir la misma modificación pendiente por dos rutas independientes. No declara rentabilidad.
- `PR111` **PASS** arranque completo OFFLINE y reinstalación de APK DEBUG preservando SharedPreferences de ensayo, run `43038549096`. No es aún prueba de migración REAL con firma histórica.
- `PR112` **PASS** fuente final Kotlin/JUnit, run `43039117348`; Android ART de código PR112 run `43039930207` pendiente de veredicto.
- `PR113` Kotlin/JUnit de dos rutas y nuevas pruebas de diario (run `43040656073`) pendiente; después falta ART e integración de red simulada de ambos gestores. Verificadores antiguos siguen activos, se actualizan solo para demostrar el nuevo flujo más estricto, no se eliminan.
- El diario permanece pendiente en caso de POST incierto y STOP remoto viejo: no se reintenta a ciegas. Sigue siendo necesario resolver sin bloqueo permanente mediante evidencia remota inequívoca (no inventar éxito).

## Antes de compilar UNA candidata final
1. Materialización canónica, todos los verificadores + Kotlin/JUnit de las fuentes finales, dos pasadas, SHA idénticos sin destrucción de parches; comprobar que no se debilitaron suites por error de compilación.
2. Unit/integración WEEX **simulada** para LONG/SHORT y validación firmada de la posición, stop vigente, TP, modifyTpSlOrder → lectura y confirmación remota → persistencia local; fallos de red, stop remoto único, idempotencia y no intervención en manuales.
3. Prueba positiva de señal válida SIM y REAL sin POST real, negativa de WAIT sin señal, recuperación tras timeout, cuenta con orden pendiente y cambio SIM/REAL sin arrastrar órdenes.
4. Android ART en emulador de la **fuente final combinada**: arranque real/servicio sin credenciales externas, 10 ciclos simulados, ANR/crashes, reconexión, recursos, no regresión VerifyError.
5. Proteger DB, Premium, saldo, aprendizaje, identidad del paquete y notificaciones. La APK nueva debe instalarse con `adb install -r` sobre una APK **original firmada** y datos de ensayo conservados; nunca `adb uninstall` en el dispositivo del propietario.
6. Revisar que el STOP del usuario no dependa de servicios remotos caducados; la supervisión de riesgo real se hará en WEEX oficial hasta completar pruebas en teléfono.
7. Generar APK release firmada **una sola vez** de commit aprobado; verificar hash, firma, paquete, número de versión y manifest; probar actualizador en simulador y comprobar acceso al asset desde fuera de GitHub.
8. **Solo después de todo lo anterior** publicar nueva release no-prerelease como GitHub latest con el nombre de asset reconocido por la app. Verificar latest real, descarga de SHA exacto y versión. Cualquier duda bloquea OTA.

NO registrar claves, tokens, comandos de trading REAL ni colocar binarios DEBUG en releases. No borrar los datos instalados ni escribir en la base de posiciones reales de pruebas.
