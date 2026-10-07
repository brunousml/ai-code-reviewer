# Configuração de Variáveis de Ambiente - Agent Review

Este documento descreve como configurar as variáveis de ambiente necessárias para o funcionamento do Agent Review na
pipeline do GitLab CI.

---

## 📋 Índice

- [Quando o Job é Executado](#quando-o-job-é-executado)
- [Local de Configuração](#local-de-configuração)
- [Variáveis Obrigatórias](#variáveis-obrigatórias)
- [Variáveis Opcionais](#variáveis-opcionais)
- [Variáveis para Controle de Execução](#variáveis-para-controle-de-execução)
  - [AGENT_REVIEW_FORCE](#7-agent_review_force)
  - [Label: agent-review-requested](#8-label-agent-review-requested)
- [Como Triggerar a Pipeline para Executar o Review](#como-triggerar-a-pipeline-para-executar-o-review)
- [Variáveis do GitLab CI (Automáticas)](#variáveis-do-gitlab-ci-automáticas)
- [Checklist de Configuração](#checklist-de-configuração)
- [Passo a Passo de Configuração](#passo-a-passo-de-configuração)
- [Testando a Configuração](#testando-a-configuração)
- [Solução de Problemas](#solução-de-problemas)
- [Segurança](#segurança)

---

## Quando o Job é Executado

O job `agent-review` tem comportamento diferente dependendo da branch de destino do Merge Request:

### MRs para `develop` (Execução Automática) ✅

- **Comportamento:** Job executa **automaticamente** na primeira vez
- **Próximos pushes:** Pula execução (idempotência - já executou)
- **Re-execução:** Via label `agent-review-requested` ou variável `AGENT_REVIEW_FORCE=true`

**Exemplo:**
```bash
# Você cria um MR: feature/new-auth → develop
✅ Pipeline executa automaticamente o job agent-review
✅ Review é publicado como comentário no MR
✅ Artefatos salvos em reviews/YYYY-MM-DD/MR_IID/

# Você faz mais commits e push
⏭️ Job detecta que já executou e pula (economiza recursos)
```

### MRs para outras branches (Execução Manual) ⚠️

- **Branches:** `master`, `release/*`, `hotfix/*`, features, etc.
- **Comportamento:** Job **NÃO executa automaticamente**
- **Como executar:** Adicione a label `agent-review-requested` ao MR

**Exemplo:**
```bash
# Você cria um MR: hotfix/critical-bug → master
⏭️ Job NÃO executa automaticamente

# Você adiciona label: agent-review-requested
✅ Próxima pipeline executa o job
✅ Label é removida automaticamente após execução
```

### Tabela Resumo

| Branch de Destino | Primeira Execução | Re-execução |
|-------------------|-------------------|-------------|
| `develop` | ✅ Automático | Via label ou variável |
| `master` | ⚠️ Via label apenas | Via label ou variável |
| `release/*` | ⚠️ Via label apenas | Via label ou variável |
| Features/outros | ⚠️ Via label apenas | Via label ou variável |

**Vantagens dessa abordagem:**
- ✅ Economia de recursos (não executa desnecessariamente em todas as branches)
- ✅ Flexibilidade total (funciona em qualquer branch quando solicitado)
- ✅ Controle do time (decide quando executar em branches críticas)

---

## Local de Configuração

**GitLab UI:** Settings > CI/CD > Variables

Ou via GitLab URL:

```
https://gitlab.example.com/group/project/-/settings/ci_cd
```

---

## Variáveis Obrigatórias

### 1. GITLAB_PRIVATE_TOKEN

**Descrição:** Token de acesso pessoal do GitLab com permissões para ler MRs, escrever comentários e gerenciar labels.

**Tipo:** Variable

- ✅ **Masked** (oculta o valor nos logs)
- ✅ **Protected** (recomendado para branches protegidos)

**Scope necessário:**

- `api` - Acesso completo à API do GitLab

**Como criar:**

1. Acesse: GitLab > User Settings > Access Tokens
   ```
   https://gitlab.example.com/-/user_settings/personal_access_tokens
   ```

2. Clique em "Add new token"

3. Preencha:
    - **Token name:** `CI Agent Review`
    - **Expiration date:** Escolha uma data futura (sugestão: 1 ano)
    - **Select scopes:** ✅ Marque `api`

4. Clique em "Create personal access token"

5. **IMPORTANTE:** Copie o token gerado (só aparece uma vez)

6. Cole o token na variável `GITLAB_PRIVATE_TOKEN` no GitLab CI/CD

**Exemplo de valor:**

```
glpat-xxxxxxxxxxxxxxxxxxxx
```

**Permissões necessárias:**

- Ler comentários de MRs
- Escrever comentários em MRs
- Ler labels de MRs
- Modificar labels de MRs (para remover `agent-review-requested`)

---

## Variáveis Opcionais

### 2. AGENT_REVIEW_REPO_URL

**Descrição:** URL do repositório Git que contém o código do agente de code review.

**Tipo:** Variable (não marcada como masked ou protected)

**Valor padrão:**

```
https://gitlab.example.com/group/ai-code-reviewer.git
```

**Quando configurar:**

- ⬜ **NÃO é necessário** configurar na maioria dos casos (usa default)
- ✅ Configure apenas se quiser usar repositório diferente
- ✅ Configure se quiser testar versão fork do agente

**Exemplo (se precisar sobrescrever):**

```
https://gitlab.example.com/seu-usuario/agent-review-fork.git
```

**Como obter:**

- URL do repositório onde o agente está hospedado
- Pode ser repositório público ou privado
- Se privado, certifique-se que `CI_JOB_TOKEN` tem acesso

---

### 3. AGENT_REVIEW_VERSION

**Descrição:** Versão (tag ou branch) do agente a ser usada.

**Tipo:** Variable (não marcada como masked ou protected)

**Valor padrão:** `v1.0.0`

**Quando configurar:**

- ⬜ **NÃO é necessário** configurar (usa default)
- ✅ Configure para usar versão específica do agente
- ✅ Configure para testar versões em desenvolvimento

**Exemplos:**

```bash
# Usar versão específica
v1.2.0

# Usar branch de desenvolvimento
main

# Usar branch de feature
feature/nova-funcionalidade
```

---

### 4. AGENT_REVIEW_LLM

**Descrição:** Define qual LLM (Large Language Model) será usado para o code review.

**Tipo:** Variable (não marcada como masked ou protected)

**Valores possíveis:**

- `openai` **(padrão)**
- `gemini`

**Valor padrão:** Se não configurada, usa `openai`

**Exemplo:**

```
gemini
```

**Observações:**

- ⚠️ Se configurar `openai`, a variável `OPENAI_API_KEY` é **obrigatória**
- ✅ Gemini é gratuito (sujeito a limites da API do Google)
- 💰 OpenAI tem custos por uso (monitore em https://platform.openai.com/usage)

**Comparação:**

| Aspecto             | OpenAI       | Gemini                 |
|---------------------|--------------|------------------------|
| **Custo**           | Pago por uso | Gratuito (com limites) |
| **Qualidade**       | Excelente    | Excelente              |
| **Velocidade**      | Rápido       | Rápido                 |
| **Disponibilidade** | Alta         | Alta                   |

---

### 5. OPENAI_API_KEY

**Descrição:** Chave de API da OpenAI para usar modelos GPT no code review.

**Tipo:** Variable

- ✅ **Masked** (oculta o valor nos logs)
- ⬜ Protected (opcional)

**Necessário quando:**

- Usar `AGENT_REVIEW_LLM=openai` (default)
- Se não configurada E `AGENT_REVIEW_LLM=openai`, o job falhará

**Como obter:**

1. Acesse: https://platform.openai.com/api-keys

2. Crie uma nova API key

3. Copie a chave (começa com `sk-proj-`)

4. Cole na variável `OPENAI_API_KEY` no GitLab CI/CD

**Exemplo de valor:**

```
sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Custos:**

- Code reviews consomem tokens da sua conta OpenAI
- Monitore o uso em: https://platform.openai.com/usage
- Custos típicos: ~$0.01 - $0.05 por review (dependendo do tamanho do MR)

---

### 6. AGENT_REVIEW_PUBLISH

**Descrição:** Controla se os comentários do review devem ser publicados no MR ou apenas gerados (dry-run).

**Tipo:** Variable (não marcada como masked ou protected)

**Valores possíveis:**

- `true` (padrão) - Publica comentários no MR
- `false` - Apenas gera review sem publicar (dry-run)

**Valor padrão:** `true`

**Quando usar `false` (dry-run):**

- 🧪 Testar o agente sem publicar comentários
- 🔍 Validar configurações
- 📊 Gerar reviews apenas para análise interna

**Exemplo:**

```
false
```

**Observação:** Em modo dry-run, o review é gerado mas não aparece no MR. Você pode ver o output nos logs do job.

---

## Variáveis para Controle de Execução

### 7. AGENT_REVIEW_FORCE

**Descrição:** Força a re-execução do agente mesmo se já tiver executado anteriormente neste MR.

**Tipo:** Variable (não marcada como masked ou protected)

**Valores possíveis:**

- `true` - Força re-execução
- `false` (padrão) - Respeita lógica de execução única

**Valor padrão:** `false`

**Quando usar:**

- ⚠️ **NÃO configure permanentemente** como variável de projeto
- ✅ Use apenas ao executar job **manualmente** quando precisar forçar nova execução
- ✅ Alternativa à label `agent-review-requested`

**Como usar:**

1. Acesse a pipeline do MR
2. Localize o job `agent-review`
3. Clique nos **três pontos ⋮** → **Run manually**
4. Adicione variável:
    - **Key:** `AGENT_REVIEW_FORCE`
    - **Value:** `true`
5. Execute o job

**Observação:** Esta variável é usada apenas para re-execução manual. Para execuções automáticas após código novo,
prefira usar a label `agent-review-requested`.

---

### 8. Label: agent-review-requested

**Descrição:** Label do GitLab que controla a execução do agente.

**Tipo:** GitLab Label (não é uma variável)

**Quando usar:**

1. **Re-executar em MRs para `develop`:**
   - Agente já executou e você quer forçar nova execução
   - Adicione a label → próxima pipeline executa → label removida automaticamente

2. **Executar pela primeira vez em outras branches:**
   - MR para `master`, `release/*`, `hotfix/*`, features, etc.
   - Job **não executa automaticamente** nessas branches
   - Adicione a label para acionar execução
   - Label removida automaticamente após execução

**Como usar:**

1. Abra o MR no GitLab
2. No menu direito, encontre "Labels"
3. Adicione: `agent-review-requested`
4. Faça push OU execute pipeline manualmente
5. ✅ Job executa
6. ✅ Label é removida automaticamente

**Exemplo - MR para master:**
```bash
# Cenário: MR hotfix/bug → master
# Job não está na pipeline

# Solução:
1. Adicione label: agent-review-requested
2. Push novo commit OU execute pipeline manualmente
3. ✅ Job aparece e executa
4. ✅ Label desaparece automaticamente
```

**Vantagens da label:**
- ✅ Mais fácil que variável manual
- ✅ Funciona para qualquer branch
- ✅ Remoção automática (não precisa limpar)
- ✅ Visível no MR (fica claro que review foi solicitado)

---

## Como Triggerar a Pipeline para Executar o Review

Existem várias formas de fazer a pipeline executar o agente de review:

### 1. Push com Label (Recomendado) ⭐

**Melhor para:** Re-executar review após adicionar label

```bash
# 1. Adicione a label no GitLab UI
# 2. Faça um push qualquer:

git push
# OU faça uma alteração simples
echo "" >> README.md
git add README.md
git commit -m "chore: trigger agent review"
git push
```

---

### 2. Empty Commit ⚡

**Melhor para:** Triggerar pipeline sem fazer mudanças no código

Um **empty commit** é um commit sem alterações que serve apenas para triggerar a pipeline.

**Quando usar:**
- ✅ Adicionou label e quer executar imediatamente
- ✅ Quer testar configuração do agent review
- ✅ Precisa re-executar pipeline sem alterar código
- ✅ Não quer fazer push de código só para testar

**Como usar:**

```bash
# Opção 1: Empty commit com mensagem descritiva
git commit --allow-empty -m "chore: trigger agent review"
git push

# Opção 2: Empty commit para re-executar review
git commit --allow-empty -m "ci: re-run agent review"
git push

# Opção 3: Empty commit após adicionar label
git commit --allow-empty -m "ci: trigger review with label"
git push
```

**Fluxo completo:**
```bash
# Cenário: MR já existe mas review não executou ou precisa re-executar

# 1. Adicione label no MR (via GitLab UI)
# 2. Execute empty commit
git commit --allow-empty -m "chore: trigger agent review"
git push

# ✅ Pipeline inicia automaticamente
# ✅ Job agent-review executa
# ✅ Label removida após execução
```

**Vantagens:**
- ✅ Não altera nenhum arquivo
- ✅ Triggera pipeline imediatamente
- ✅ Fica registrado no histórico Git
- ✅ Ideal para testes

**Desvantagens:**
- ⚠️ Adiciona commit "vazio" ao histórico
- ⚠️ Requer push (consome 1 slot de pipeline)

---

### 3. Executar Pipeline Manualmente no GitLab UI

**Melhor para:** Executar sem fazer nenhum commit

**Como usar:**

1. Acesse o MR no GitLab
2. Aba **"Pipelines"**
3. Botão **"Run pipeline"**
4. Selecione a branch do MR
5. Clique em **"Run pipeline"**

**Vantagens:**
- ✅ Não cria commit
- ✅ Não altera histórico Git
- ✅ Executa imediatamente

**Desvantagens:**
- ⚠️ Precisa acessar GitLab UI
- ⚠️ Mais cliques que empty commit

---

### 4. Job Manual com Variável

**Melhor para:** Forçar re-execução sem label

**Como usar:**

1. Acesse Pipeline → Jobs
2. Localize `agent-review`
3. ⋮ → **"Run manually"**
4. Adicione variável:
   - Key: `AGENT_REVIEW_FORCE`
   - Value: `true`
5. Execute

**Quando usar:**
- ✅ Job já executou mas quer forçar novamente
- ✅ Não quer adicionar label
- ✅ Testar sem modificar MR

---

### Tabela Comparativa

| Método | Altera Código | Precisa UI | Velocidade | Recomendado Para |
|--------|---------------|------------|------------|------------------|
| **Push com label** ⭐ | ✅ Sim | ✅ Sim (label) | ⚡⚡ Rápido | Re-executar com mudanças |
| **Empty commit** ⚡ | ❌ Não | ❌ Não | ⚡⚡⚡ Muito rápido | Trigger rápido sem mudanças |
| **Pipeline manual** | ❌ Não | ✅ Sim | ⚡ Médio | Executar sem commit |
| **Job manual** | ❌ Não | ✅ Sim | ⚡ Médio | Forçar sem label |

---

### Exemplos Práticos

**Cenário 1: Adicionou label e quer executar agora**
```bash
# Forma mais rápida: Empty commit
git commit --allow-empty -m "ci: trigger agent review"
git push
```

**Cenário 2: Quer testar configuração do agent**
```bash
# Empty commit para não alterar código
git commit --allow-empty -m "test: validating agent review setup"
git push
```

**Cenário 3: Re-executar após fix no código**
```bash
# Push normal (código já mudou)
git add .
git commit -m "fix: corrige bug apontado no review"
git push
# Label já está no MR → executa automaticamente
```

---

## Variáveis do GitLab CI (Automáticas)

Estas variáveis são fornecidas automaticamente pelo GitLab CI e **NÃO precisam ser configuradas manualmente:**

| Variável                              | Descrição                            | Exemplo                                    |
|---------------------------------------|--------------------------------------|--------------------------------------------|
| `CI_SERVER_URL`                       | URL do servidor GitLab               | `https://gitlab.example.com`                     |
| `CI_PROJECT_PATH`                     | Path completo do projeto             | `group/project`                           |
| `CI_MERGE_REQUEST_IID`                | ID interno do MR                     | `123`                                      |
| `CI_PIPELINE_SOURCE`                  | Origem da pipeline                   | `merge_request_event`                      |
| `CI_MERGE_REQUEST_TARGET_BRANCH_NAME` | Branch de destino do MR              | `develop`                                  |
| `CI_MERGE_REQUEST_LABELS`             | Labels do MR (separadas por vírgula) | `bug,high-priority,agent-review-requested` |
| `CI_JOB_TOKEN`                        | Token temporário do job              | (gerado automaticamente)                   |
| `GITLAB_URL`                          | URL do GitLab (fallback)             | `https://gitlab.example.com`                     |

**Nota sobre `CI_JOB_TOKEN`:**

- Usado para clonar o repositório do agente de forma segura
- Token temporário válido apenas durante o job
- Não aparece em logs (configuração segura implementada)

---

## Checklist de Configuração

Use este checklist para garantir que todas as variáveis estão configuradas:

### Obrigatórias

- [x] `GITLAB_PRIVATE_TOKEN` - Token de acesso GitLab (masked) ✅ **OBRIGATÓRIO**

### Opcionais (mas recomendadas)

- [ ] `OPENAI_API_KEY` - Chave API OpenAI (masked) - **OBRIGATÓRIO se `AGENT_REVIEW_LLM=openai`**
- [ ] `AGENT_REVIEW_LLM` - Escolha do LLM (`openai` ou `gemini`)

### Opcionais (avançadas)

- [ ] `AGENT_REVIEW_REPO_URL` - URL do repositório do agente (somente se usar fork)
- [ ] `AGENT_REVIEW_VERSION` - Versão do agente (somente se precisar versão específica)
- [ ] `AGENT_REVIEW_PUBLISH` - Publicar comentários (somente para dry-run)

### Validação

- [ ] Token GitLab está marcado como **masked** ✅
- [ ] Token GitLab tem scope `api` ✅
- [ ] Token GitLab tem acesso ao projeto ✅
- [ ] Se usar OpenAI, a API key está **masked** ✅
- [ ] Se usar OpenAI, a API key está válida e tem créditos ✅

---

## Passo a Passo de Configuração

### 1. Acessar Configurações de CI/CD

1. Navegue até o projeto no GitLab: `https://gitlab.example.com/group/project`
2. Clique em **Settings** (menu lateral esquerdo)
3. Clique em **CI/CD**
4. Expanda a seção **Variables**

### 2. Adicionar Variável Obrigatória

**GITLAB_PRIVATE_TOKEN:**

1. Clique em **Add variable**
2. Preencha:
    - **Key:** `GITLAB_PRIVATE_TOKEN`
    - **Value:** `glpat-xxxxxxxxxxxxxxxxxxxx` (seu token)
    - **Type:** Variable
    - **Environment scope:** All (não protegido)
    - **Flags:**
        - ✅ **Masked**
        - ✅ Protected (opcional, mas recomendado)
        - ⬜ Expand variable reference
3. Clique em **Add variable**

### 3. Adicionar Variáveis Opcionais (se necessário)

**Se usar OpenAI (default):**

1. Clique em **Add variable**
2. Preencha:
    - **Key:** `OPENAI_API_KEY`
    - **Value:** `sk-proj-xxxxxxxxxxxx` (sua chave)
    - **Type:** Variable
    - **Environment scope:** All
    - **Flags:**
        - ✅ **Masked**
        - ⬜ Protected
        - ⬜ Expand variable reference
3. Clique em **Add variable**

**Se preferir usar Gemini (gratuito):**

1. Clique em **Add variable**
2. Preencha:
    - **Key:** `AGENT_REVIEW_LLM`
    - **Value:** `gemini`
    - **Type:** Variable
    - **Environment scope:** All
    - **Flags:** (nenhum marcado)
3. Clique em **Add variable**

### 4. Verificar Configuração

Após adicionar as variáveis, você deve ter no mínimo:

**Configuração Mínima (usando OpenAI):**

```
GITLAB_PRIVATE_TOKEN     glpat-***************     All    masked
OPENAI_API_KEY          sk-proj-*************     All    masked
```

**Configuração Mínima (usando Gemini - gratuito):**

```
GITLAB_PRIVATE_TOKEN     glpat-***************     All    masked
AGENT_REVIEW_LLM        gemini                    All    (no flags)
```

---

## Testando a Configuração

### 1. Criar um MR de Teste

1. Crie uma branch de teste:
   ```bash
   git checkout -b test/agent-review
   ```

2. Faça uma alteração simples:
   ```bash
   echo "# Test" >> README.md
   git add README.md
   git commit -m "test: validar agent-review"
   git push origin test/agent-review
   ```

3. Abra um MR para `develop` (execução automática) **OU** para outra branch com label `agent-review-requested`

**Opção A - Testar com `develop` (automático):**
```bash
# Cria MR: test/agent-review → develop
✅ Job executa automaticamente
```

**Opção B - Testar com `master` (manual):**
```bash
# Cria MR: test/agent-review → master
⚠️ Job NÃO executa

# Adicione label: agent-review-requested
✅ Job executa na próxima pipeline
```

### 2. Verificar a Pipeline

1. Acesse a pipeline do MR
2. Procure pelo job `agent-review`
3. Clique no job para ver os logs

### 3. Logs Esperados

**✅ Sucesso (Primeira Execução):**

```
ℹ️ === GitLab Agent Review ===
ℹ️ Iniciando processo de code review automatizado...
✅ Verificando variáveis obrigatórias...
✅ Verificando dependências...
ℹ️ Verificando se já existe review anterior neste MR...
ℹ️ Nenhum review anterior encontrado ✨
ℹ️ Clonando repositório do agente (tag/branch: v1.0.0) usando token de CI... 📥
ℹ️ Repositório clonado com sucesso em: /tmp/tmp.XXXXXX/agent-review
ℹ️ Configurando ambiente Python... 🐍
ℹ️ Atualizando pip... ⬆️
ℹ️ Instalando dependências do requirements.txt...
ℹ️ Ambiente Python configurado com sucesso! ✅
ℹ️ Configurando variáveis de ambiente para o agente... ⚙️
ℹ️ Arquivo .env criado. 📝
ℹ️ Executando code review... 🤖
ℹ️ URL do MR: https://gitlab.example.com/group/project/-/merge_requests/123
ℹ️ LLM selecionado: openai
ℹ️ Publicar comentários: true
ℹ️ Code review executado com sucesso! 🎉
ℹ️ === Processo concluído com sucesso! ✨ ===
```

**✅ Sucesso (Segunda Execução - Skip):**

```
ℹ️ === GitLab Agent Review ===
ℹ️ Iniciando processo de code review automatizado...
✅ Verificando variáveis obrigatórias...
✅ Verificando dependências...
ℹ️ Verificando se já existe review anterior neste MR...
ℹ️ Review anterior encontrado neste MR ✅
🛑 Agente já executou review neste MR anteriormente
💡 Para executar novamente, use uma das opções:
   1. Execute o job manualmente com variável AGENT_REVIEW_FORCE=true
   2. Adicione a label 'agent-review-requested' ao MR
ℹ️ Pulando execução... ⏭️
ℹ️ === Processo concluído com sucesso! ✨ ===
```

**❌ Erro - Variável Faltando:**

```
❌ Variáveis de ambiente obrigatórias não configuradas:
  - GITLAB_PRIVATE_TOKEN
```

**❌ Erro - OpenAI API Key Faltando:**

```
❌ Variáveis de ambiente obrigatórias não configuradas:
  - OPENAI_API_KEY (obrigatório para o LLM 'openai')
```

---

## Solução de Problemas

### ❌ Erro: "GITLAB_PRIVATE_TOKEN não configurada"

**Causa:** Token do GitLab não configurado

**Solução:**

1. Vá em Settings → CI/CD → Variables
2. Adicione `GITLAB_PRIVATE_TOKEN` com valor do seu token
3. Marque como **masked**
4. Execute pipeline novamente

---

### ❌ Erro: "OPENAI_API_KEY não configurada" (se usar OpenAI)

**Causa:** API Key da OpenAI não configurada quando `AGENT_REVIEW_LLM=openai`

**Solução 1 (usar OpenAI):**

1. Obtenha API Key em https://platform.openai.com/api-keys
2. Adicione variável `OPENAI_API_KEY` (masked)
3. Execute pipeline novamente

**Solução 2 (usar Gemini - gratuito):**

1. Adicione variável `AGENT_REVIEW_LLM` com valor `gemini`
2. Execute pipeline novamente

---

### ❌ Erro: "curl não encontrado"

**Causa:** Dependência `curl` faltando (improvável após atualização)

**Solução:**

- Já corrigido na versão atual do script
- Verifique se `.gitlab-ci.yml:34` contém: `apk add --no-cache git build-base python3-dev curl`

---

### ❌ Erro: "Falha ao clonar repositório do agente"

**Causas possíveis:**

- `AGENT_REVIEW_REPO_URL` incorreta
- `CI_JOB_TOKEN` sem permissão para acessar o repositório
- Repositório do agente inacessível
- Versão/tag especificada não existe

**Solução:**

1. Verifique se a URL está correta (default: `https://gitlab.example.com/group/ai-code-reviewer.git`)
2. Se usar fork, verifique se o repositório é acessível
3. Verifique se `AGENT_REVIEW_VERSION` existe no repositório
4. Teste clonar manualmente:
   ```bash
   git clone https://gitlab.example.com/group/ai-code-reviewer.git
   git ls-remote --tags https://gitlab.example.com/group/ai-code-reviewer.git
   ```

---

### ❌ Erro: "Falha ao executar code review" com OpenAI

**Causas possíveis:**

- `OPENAI_API_KEY` inválida ou expirada
- Sem créditos na conta OpenAI
- Rate limit excedido
- API da OpenAI indisponível

**Solução:**

1. Verifique a validade da API key em https://platform.openai.com/api-keys
2. Verifique créditos em: https://platform.openai.com/usage
3. Aguarde alguns minutos se for rate limit
4. Considere usar `AGENT_REVIEW_LLM=gemini` temporariamente

---

### ⚠️ Job não é executado

**Causas possíveis:**

- MR tem target branch diferente de `develop` e **não tem a label** `agent-review-requested`
- Pipeline não foi criada como `merge_request_event`
- Job já executou e está pulando (comportamento esperado - idempotência)

**Solução:**

1. **Para MRs com target `develop`:**
   - Verifique se a pipeline foi disparada por um MR
   - Se já executou, veja logs para confirmar se foi skip intencional
   - Para re-executar, adicione label `agent-review-requested` ou use `AGENT_REVIEW_FORCE=true`

2. **Para MRs com outras branches** (`master`, `release`, etc.):
   - ✅ **Adicione a label** `agent-review-requested` ao MR
   - Execute pipeline novamente (ou faça push)
   - Job executará quando detectar a label
   - Label será removida automaticamente após execução

**Exemplo - MR para master:**
```bash
# MR: hotfix/bug → master
# Job não aparece na pipeline

# Solução:
1. Adicione label: agent-review-requested
2. Faça novo push OU execute pipeline manualmente
3. ✅ Job executa
4. Label removida automaticamente
```

---

### 🔁 Agente executou múltiplas vezes sem querer

**Causa:** Label `agent-review-requested` não foi removida automaticamente

**Solução:**

1. Verifique se label `agent-review-requested` ainda está no MR
2. Remova manualmente a label
3. Verifique logs do job para ver se remoção automática falhou
4. Se problema persistir, verifique se `GITLAB_PRIVATE_TOKEN` tem permissão para modificar labels

---

## Segurança

### Boas Práticas

1. **SEMPRE marque tokens e API keys como masked:**
    - `GITLAB_PRIVATE_TOKEN` ✅ **masked**
    - `OPENAI_API_KEY` ✅ **masked**
    - `AGENT_REVIEW_FORCE` ⬜ não precisa ser masked
    - `AGENT_REVIEW_LLM` ⬜ não precisa ser masked

2. **Rotacione tokens periodicamente:**
    - Tokens GitLab: a cada 3-6 meses
    - API keys OpenAI: conforme a política da sua organização

3. **Use tokens com escopo mínimo:**
    - Token GitLab: apenas scope `api` (não use `read_api`, `write_repository`, etc.)
    - Não use tokens pessoais de admin/owner

4. **Monitore o uso:**
    - Logs do GitLab CI
    - Usage da OpenAI (se usar): https://platform.openai.com/usage
    - Custos de API

5. **Não commite secrets:**
    - Nunca adicione tokens ao código
    - Use apenas variáveis de CI/CD
    - Verifique com git-secrets ou similar

6. **Autenticação segura para clone:**
    - Script usa `git config` temporário (não expõe token na URL)
    - Configuração é removida imediatamente após uso
    - Output é filtrado para remover referências ao token

### Token Seguro no Git Clone

A versão atual implementa autenticação segura:

```bash
# ✅ SEGURO (implementado)
git config --global url."https://gitlab-ci-token:${CI_JOB_TOKEN}@${host}/".insteadOf "https://${host}/"
git clone -q <url>
git config --global --unset url."...".insteadOf

# ❌ INSEGURO (NÃO usado)
git clone https://gitlab-ci-token:${CI_JOB_TOKEN}@<url>
```

**Vantagens:**

- Token não aparece em comandos nos logs
- Configuração é temporária (removida após uso)
- Output filtrado para remover referências ao token
- Compatível com todas as versões do GitLab

---

## Variáveis Resumidas

### Configuração Completa (Todas as Opções)

| Variável                | Obrigatória      | Default                                                 | Masked | Descrição                                    |
|-------------------------|------------------|---------------------------------------------------------|--------|----------------------------------------------|
| `GITLAB_PRIVATE_TOKEN`  | ✅ Sim            | -                                                       | ✅ Sim  | Token GitLab com scope `api`                 |
| `OPENAI_API_KEY`        | ⚠️ Se LLM=openai | -                                                       | ✅ Sim  | API Key da OpenAI                            |
| `AGENT_REVIEW_LLM`      | ⬜ Não            | `openai`                                                | ⬜ Não  | LLM a usar (`openai`/`gemini`)               |
| `AGENT_REVIEW_REPO_URL` | ⬜ Não            | `https://gitlab.example.com/group/ai-code-reviewer.git` | ⬜ Não  | URL do repositório do agente                 |
| `AGENT_REVIEW_VERSION`  | ⬜ Não            | `v1.0.0`                                                | ⬜ Não  | Versão/tag do agente                         |
| `AGENT_REVIEW_PUBLISH`  | ⬜ Não            | `true`                                                  | ⬜ Não  | Publicar comentários (`true`/`false`)        |
| `AGENT_REVIEW_FORCE`    | ⬜ Não            | `false`                                                 | ⬜ Não  | Forçar re-execução (usar apenas manualmente) |

---

## Referências

- [GitLab CI/CD Variables](https://docs.gitlab.com/ee/ci/variables/)
- [GitLab Personal Access Tokens](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html)
- [GitLab Predefined Variables](https://docs.gitlab.com/ee/ci/variables/predefined_variables.html)
- [OpenAI API Keys](https://platform.openai.com/api-keys)
- [Google Gemini API](https://ai.google.dev/)

---

**Última atualização:** 2025-10-30
**Versão:** 2.0.0
