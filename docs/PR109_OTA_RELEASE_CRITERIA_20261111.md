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
