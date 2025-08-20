param(
	[string]$Owner = "KimJin777",
	[string]$Repo = "aibitcoin",
	[string]$Head = "뉴스-활용",
	[string]$Base = "main",
	[string]$Title = "feat(main): 손절매 조건 hold 시에만 실행 + 테스트/README/cleanup/DB 보정",
	[string]$Body = "자동 PR 생성: 손절매 조건 보유 신호일 때만 실행하도록 변경, tests 폴더 정리, README/cleanup.bat 추가, DB news 스키마 보정"
)

$ErrorActionPreference = 'Stop'

if (-not $env:GH_TOKEN) {
	Write-Error "GH_TOKEN 환경 변수가 설정되어 있지 않습니다. repo 권한을 가진 GitHub Personal Access Token을 설정하세요."
	exit 1
}

$Headers = @{
	Authorization = "token $($env:GH_TOKEN)"
	"Accept"    = "application/vnd.github+json"
	"X-GitHub-Api-Version" = "2022-11-28"
}

function New-GitHubPullRequest {
	param(
		[string]$Owner,
		[string]$Repo,
		[string]$Title,
		[string]$Head,
		[string]$Base,
		[string]$Body
	)
	$Uri = "https://api.github.com/repos/$Owner/$Repo/pulls"
	$Payload = @{ title=$Title; head=$Head; base=$Base; body=$Body; maintainer_can_modify=$true; draft=$false }
	return Invoke-RestMethod -Method Post -Uri $Uri -Headers $Headers -Body ($Payload | ConvertTo-Json) -ContentType 'application/json'
}

function Merge-GitHubPullRequest {
	param(
		[string]$Owner,
		[string]$Repo,
		[int]$Number,
		[string]$MergeMethod = 'merge'
	)
	$Uri = "https://api.github.com/repos/$Owner/$Repo/pulls/$Number/merge"
	$Payload = @{ merge_method=$MergeMethod }
	return Invoke-RestMethod -Method Put -Uri $Uri -Headers $Headers -Body ($Payload | ConvertTo-Json) -ContentType 'application/json'
}

function Remove-GitHubBranch {
	param(
		[string]$Owner,
		[string]$Repo,
		[string]$Branch
	)
	$RefPath = "heads/$Branch"
	$EncodedRef = [uri]::EscapeDataString($RefPath)
	$Uri = "https://api.github.com/repos/$Owner/$Repo/git/refs/$EncodedRef"
	Invoke-RestMethod -Method Delete -Uri $Uri -Headers $Headers | Out-Null
}

try {
	Write-Host "[PR] Creating pull request: $Owner/$Repo $Head -> $Base"
	$pr = New-GitHubPullRequest -Owner $Owner -Repo $Repo -Title $Title -Head $Head -Base $Base -Body $Body
	$prNumber = $pr.number
	$prUrl = $pr.html_url
	Write-Host "[PR] Created: #$prNumber $prUrl"

	Write-Host "[PR] Merging PR #$prNumber..."
	$merge = Merge-GitHubPullRequest -Owner $Owner -Repo $Repo -Number $prNumber -MergeMethod 'merge'
	if ($merge.merged -ne $true) { throw "Merge failed: $($merge.message)" }
	Write-Host "[PR] Merged successfully"

	Write-Host "[PR] Deleting branch '$Head'..."
	Remove-GitHubBranch -Owner $Owner -Repo $Repo -Branch $Head
	Write-Host "[PR] Branch deleted"

	Write-Host "[PR] Done."
} catch {
	Write-Error $_
	exit 1
}
