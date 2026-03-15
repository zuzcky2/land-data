#!/bin/bash
# ============================================================
# 새 맥북 개발 환경 세팅 스크립트
# 사전 조건: Tailscale 설치 후 jjambbongjoa@ 계정으로 로그인
#
# 실행 방법:
#   curl -fsSL https://raw.githubusercontent.com/zuzcky2/land-data/master/setup_new_mac.sh | bash
#   또는 repo clone 후: bash setup_new_mac.sh
# ============================================================

set -e

DEV_TS="100.96.88.2"
DEV_USER="kjs"
REPO_URL="git@github.com:zuzcky2/land-data.git"
LOCAL_PROJECT="$HOME/workspace/landmark/land-data"
PROJECT_KEY="-Users-kjs-workspace-landmark-land-data"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
ok()   { echo -e "${GREEN}✅ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
fail() { echo -e "${RED}❌ $1${NC}"; exit 1; }

echo ""
echo "🚀 새 맥북 개발 환경 세팅 시작"
echo "=============================="

# ── 1. Tailscale 확인 ──────────────────────────────────────
echo ""
echo "1️⃣  Tailscale 확인"
if ! command -v tailscale &>/dev/null; then
  fail "Tailscale이 없습니다. https://tailscale.com/download 에서 설치 후 다시 실행하세요."
fi
if ! tailscale status &>/dev/null; then
  fail "Tailscale이 연결되지 않았습니다. 'tailscale up' 실행 후 jjambbongjoa@ 계정으로 로그인하세요."
fi
TAILSCALE_SELF=$(tailscale status --json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('Self',{}).get('HostName',''))" 2>/dev/null || echo "")
ok "Tailscale 연결됨 ($TAILSCALE_SELF)"

# ── 2. 개발 서버 접속 확인 ─────────────────────────────────
echo ""
echo "2️⃣  개발 서버 접속 확인"
if ! ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no \
        -o PasswordAuthentication=no \
        -i "$HOME/.ssh/id_rsa_dev" \
        ${DEV_USER}@${DEV_TS} "echo ok" &>/dev/null; then
  warn "SSH 키 없음 → 개발 서버에서 키 복사 시도 중..."

  # 개발서버에서 SSH 키 가져오기 (Tailscale 통해 비밀번호 인증)
  mkdir -p ~/.ssh && chmod 700 ~/.ssh
  echo "   개발 서버 비밀번호를 입력하세요:"
  scp -o StrictHostKeyChecking=no \
      ${DEV_USER}@${DEV_TS}:~/.ssh/mac_backup/id_rsa_dev ~/.ssh/id_rsa_dev
  scp -o StrictHostKeyChecking=no \
      ${DEV_USER}@${DEV_TS}:~/.ssh/mac_backup/id_rsa_dev.pub ~/.ssh/id_rsa_dev.pub
  chmod 600 ~/.ssh/id_rsa_dev
  ok "SSH 키 복사 완료"
else
  ok "SSH 키 이미 존재함"
fi

# ── 3. SSH config 설정 ─────────────────────────────────────
echo ""
echo "3️⃣  SSH config 설정"
if ! grep -q "Host dev-ts" ~/.ssh/config 2>/dev/null; then
  cat >> ~/.ssh/config <<EOF

Host dev
    HostName 192.168.219.120
    User kjs
    IdentityFile ~/.ssh/id_rsa_dev
    Port 22

Host dev-ts
    HostName 100.96.88.2
    User kjs
    IdentityFile ~/.ssh/id_rsa_dev
    Port 22
EOF
  chmod 600 ~/.ssh/config
  ok "SSH config 추가됨"
else
  ok "SSH config 이미 설정됨"
fi

# ── 4. 개발 서버 접속 재확인 ───────────────────────────────
ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no \
    dev-ts "echo ok" &>/dev/null || fail "개발 서버 SSH 접속 실패"
ok "개발 서버 접속 확인"

# ── 5. Homebrew 확인 ───────────────────────────────────────
echo ""
echo "4️⃣  Homebrew 확인"
if ! command -v brew &>/dev/null; then
  warn "Homebrew 없음 → 설치 중..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi
ok "Homebrew 준비됨"

# ── 6. Git 확인 ────────────────────────────────────────────
echo ""
echo "5️⃣  Git 확인"
if ! command -v git &>/dev/null; then
  brew install git
fi
ok "Git 준비됨"

# ── 7. 레포 클론 ───────────────────────────────────────────
echo ""
echo "6️⃣  레포 클론"
mkdir -p "$HOME/workspace/landmark"
if [ -d "$LOCAL_PROJECT/.git" ]; then
  ok "이미 클론됨 → git pull"
  git -C "$LOCAL_PROJECT" pull
else
  git clone "$REPO_URL" "$LOCAL_PROJECT"
  ok "클론 완료: $LOCAL_PROJECT"
fi

# ── 8. Claude 컨텍스트 복원 ────────────────────────────────
echo ""
echo "7️⃣  Claude 컨텍스트 복원"
CLAUDE_PROJECT_DIR="$HOME/.claude/projects/$PROJECT_KEY"
mkdir -p "$CLAUDE_PROJECT_DIR"

# memory 동기화 (서버 → 새 맥북)
rsync -az --delete \
    ${DEV_USER}@${DEV_TS}:~/claude_sync/memory/ \
    "$CLAUDE_PROJECT_DIR/memory/"
ok "Memory 파일 복원됨"

# 대화 JSONL 복원 (이어서 대화 가능)
CONV_FILE="$CLAUDE_PROJECT_DIR/09f808ab-b4ae-4101-84ec-7ba5106dec68.jsonl"
if [ ! -f "$CONV_FILE" ]; then
  rsync -az \
      ${DEV_USER}@${DEV_TS}:~/claude_sync/conversation.jsonl \
      "$CONV_FILE"
  ok "대화 기록 복원됨"
else
  ok "대화 기록 이미 존재함"
fi

# ── 완료 ───────────────────────────────────────────────────
echo ""
echo "=============================="
echo -e "${GREEN}🎉 세팅 완료!${NC}"
echo ""
echo "다음 명령으로 작업을 이어서 시작하세요:"
echo "  cd $LOCAL_PROJECT"
echo "  claude"
echo ""
echo "개발 서버 접속:"
echo "  ssh dev-ts   # 어디서든 (Tailscale)"
echo "  ssh dev      # 홈 네트워크 내부"
echo ""
