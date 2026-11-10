#!/usr/bin/env python3
"""Stage EXACT CircleCI PR102 signed artifact; never build, trade, or publish OTA."""
import hashlib,json,os,re,subprocess,urllib.request,urllib.parse,zipfile
from pathlib import Path
JOB="d466261a-bb7d-46fc-b419-d602f42d2efb"
SHA="375a2d9a3cf7f58bfebdd3182e098c1dd6609d15"
BRANCH="repair/integrated-entry-plan-close-resume-20261109"
REPO="wilitohtc24-jpg/weex-auto-trader-android"
SIGNER="5d0698ff9d09d7928944d01260d30b277ca4d20bd52c6cc583147b436b6c22e6"
NAMES=["WEEX-IA-Trader-release.apk","release.json","signing-certificate.txt","apk-sha256.txt","candidate-provenance.txt","release-coverage.json"]
C=os.environ.get("WEEX_CIRCLECI_ARTIFACT_READ_TOKEN","")
G=os.environ.get("WEEX_SOURCE_RELEASE_READ_TOKEN","")
OUT=Path("private-pr102-candidate")
def fail(reason):raise SystemExit("PR102_EXACT_ARTIFACT_BLOCKED: "+reason)
def get(url,token,github=False):
    headers={"User-Agent":"WEEX-Artifacts/1","Accept":"application/json"}
    headers["Authorization" if github else "Circle-Token"]=("Bearer " if github else "")+token
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=30) as r:
            return json.load(r)
    except Exception as e:fail("API_READ_"+type(e).__name__)
def android_tool(name):
    for root in (os.environ.get("ANDROID_HOME"),os.environ.get("ANDROID_SDK_ROOT")):
        if root:
            matches=sorted((Path(root)/"build-tools").glob("*/"+name))
            if matches:return str(matches[-1])
    fail("ANDROID_TOOL_MISSING_"+name)
if not C or not G:fail("API_CREDENTIAL_MISSING")
if get("https://api.github.com/repos/"+REPO+"/commits/"+SHA,G,True).get("sha")!=SHA:
    fail("PRIVATE_SOURCE_SHA_MISMATCH")
job=get("https://circleci.com/api/v2/jobs/"+JOB,C)
if job.get("id")!=JOB or job.get("name")!="pr102_private_candidate" or job.get("status")!="success":
    fail("EXACT_CIRCLECI_JOB_ID_NAME_OR_STATUS_MISMATCH")
# The UUID job endpoint returns project_id, NOT project_slug. CircleCI's
# workflow jobs endpoint provides the project_slug required by the artifacts API.
workflow_id=job.get("workflow_id")
if not isinstance(workflow_id,str) or not re.fullmatch(r"[0-9a-fA-F-]{36}",workflow_id):
    fail("CIRCLECI_WORKFLOW_ID_MISSING")
matching=[];workflow_page=None
while True:
    workflow_url="https://circleci.com/api/v2/workflow/"+workflow_id+"/job"
    if workflow_page:workflow_url+="?page-token="+urllib.parse.quote(workflow_page,safe="")
    workflow_jobs=get(workflow_url,C)
    matching.extend(x for x in workflow_jobs.get("items",[]) if x.get("id")==JOB)
    if len(matching)>1:fail("CIRCLECI_DUPLICATE_EXACT_JOB")
    workflow_page=workflow_jobs.get("next_page_token")
    if not workflow_page:break
if len(matching)!=1:fail("CIRCLECI_EXACT_WORKFLOW_JOB_NOT_FOUND")
workflow_job=matching[0]
if workflow_job.get("status")!="success" or workflow_job.get("name")!="pr102_private_candidate":
    fail("CIRCLECI_WORKFLOW_JOB_MISMATCH")
slug,num=workflow_job.get("project_slug"),workflow_job.get("job_number")
if num!=job.get("job_number") or not isinstance(slug,str) or not re.fullmatch(r"[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+",slug) or not isinstance(num,int):
    fail("CIRCLECI_PROJECT_OR_NUMBER_MISSING")
all_items=[];page=None
while True:
    url=f"https://circleci.com/api/v2/project/{slug}/{num}/artifacts"
    if page:url+="?page-token="+urllib.parse.quote(page,safe="")
    x=get(url,C)
    all_items.extend(x.get("items",[]))
    if len(all_items)>1000:fail("UNEXPECTED_ARTIFACT_LIST")
    page=x.get("next_page_token")
    if not page:break
OUT.mkdir(parents=True,exist_ok=True)
for name in NAMES:
    matches=[x for x in all_items if str(x.get("path","")).endswith("private-pr102-candidate/"+name)]
    if len(matches)!=1:fail("ARTIFACT_MISSING_OR_DUPLICATE_"+name)
    url=matches[0].get("url","")
    p=urllib.parse.urlparse(url)
    if p.scheme!="https" or not p.hostname:fail("INVALID_ARTIFACT_URL_"+name)
    # Artifact URL is a short-lived presigned CircleCI link. Never forward
    # the CircleCI API token to an external download hostname.
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"WEEX-Artifacts/1"}),timeout=180) as r, (OUT/name).open("wb") as dst:
            total=0
            while True:
                chunk=r.read(1024*1024)
                if not chunk:break
                total+=len(chunk)
                if total>250_000_000:fail("OVERSIZED_ARTIFACT_"+name)
                dst.write(chunk)
    except Exception as e:fail("ARTIFACT_DOWNLOAD_"+name+"_"+type(e).__name__)
    if not total:fail("EMPTY_ARTIFACT_"+name)
    print("PRIVATE_ARTIFACT_DOWNLOADED",name,total)
apk=OUT/NAMES[0]
with apk.open("rb") as stream:digest=hashlib.file_digest(stream,"sha256").hexdigest()
meta=json.loads((OUT/"release.json").read_text())
version=meta.get("versionCode")
if (meta.get("sourceCommit")!=SHA or meta.get("sourceBranch")!=BRANCH or meta.get("packageName")!="com.wilito.weexautotrader" or meta.get("signerSha256")!=SIGNER):
    fail("RELEASE_SOURCE_AND_SIGNER_MISMATCH")
if not isinstance(version,int) or version<=29176085:fail("VERSION_NOT_NEWER")
if meta.get("sha256")!=digest or meta.get("sizeBytes")!=apk.stat().st_size:fail("RELEASE_SHA_SIZE_MISMATCH")
if digest not in (OUT/"apk-sha256.txt").read_text():fail("RELEASE_DIGEST_FILE_MISMATCH")
if SIGNER not in (OUT/"signing-certificate.txt").read_text().lower():fail("ORIGINAL_SIGNER_REPORT_MISSING")
provenance=(OUT/"candidate-provenance.txt").read_text()
if "source="+SHA not in provenance or "ota_publication=false" not in provenance:fail("PR102_PROVENANCE_MISMATCH")
if not zipfile.is_zipfile(apk):fail("APK_ZIP_INVALID")
with zipfile.ZipFile(apk) as z:
    if z.testzip() is not None:fail("APK_ZIP_CORRUPTED")
sig=subprocess.run([android_tool("apksigner"),"verify","--print-certs",str(apk)],text=True,capture_output=True,check=True).stdout.lower()
if SIGNER not in sig:fail("BINARY_APK_SIGNER_MISMATCH")
badging=subprocess.run([android_tool("aapt"),"dump","badging",str(apk)],text=True,capture_output=True,check=True).stdout
m=re.search(r"package: name='([^']+)' versionCode='(\d+)'",badging)
if not m or m.group(1)!="com.wilito.weexautotrader" or int(m.group(2))!=version:fail("BINARY_APK_PACKAGE_OR_VERSION_MISMATCH")
with Path(os.environ["GITHUB_OUTPUT"]).open("a") as f:
    f.write(f"version={version}\nsha256={digest}\nbytes={apk.stat().st_size}\n")
print("PR102_EXACT_APK_VERIFIED_FROM_CIRCLECI",version,digest,apk.stat().st_size)
print("NO_REAL_ORDERS_NO_REBUILD_NO_PUBLIC_OTA")
