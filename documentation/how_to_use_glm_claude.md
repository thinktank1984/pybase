how to connect glm4.6 to claude code
You said:
make perm export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
export ANTHROPIC_AUTH_TOKEN="YOUR_ZAI_API_KEY"
# Optionally override default models
export ANTHROPIC_DEFAULT_OPUS_MODEL="glm-4.6"
export ANTHROPIC_DEFAULT_SONNET_MODEL="glm-4.6"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="glm-4.5-air"
You said:
use echo to add it to bash linux
You said:
echo '
# Claude Code + GLM 4.6 integration (Z.ai)
export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
export ANTHROPIC_AUTH_TOKEN="b0d8bc10b7274fde891719c0f5fae80a.227yTm8wFgBMcyJW"
export ANTHROPIC_DEFAULT_OPUS_MODEL="glm-4.6"
export ANTHROPIC_DEFAULT_SONNET_MODEL="glm-4.6"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="glm-4.5-air"
' >> ~/.bashrc

claude code does not recognize, how to fix???


ChatGPT can make mistakes. Check important info.