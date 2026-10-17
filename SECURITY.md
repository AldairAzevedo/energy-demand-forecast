# Diretrizes de Segurança (Security Policy)

Este documento estabelece as políticas de segurança, suporte a versões e procedimentos para reporte responsável de vulnerabilidades no projeto **energy-demand-forecast**.

---

## 1. Versões com Suporte (Supported Versions)

Apenas a versão mais recente em desenvolvimento na branch `main` recebe ativamente correções de segurança e patches operacionais.

| Versão | Suporte Ativo | Notas |
| :--- | :---: | :--- |
| `1.0.x` (`main`) | :white_check_mark: Sim | Versão oficial com suíte de testes e validação completa |
| `< 1.0.0` | :x: Não | Versões experimentais ou rascunhos de desenvolvimento |

---

## 2. Reportando uma Vulnerabilidade (Reporting a Vulnerability)

Levamos a integridade e segurança do software a sério. Caso você identifique qualquer vulnerabilidade de segurança, falha de integridade de dados ou vazamento potencial de credenciais, pedimos que siga o processo de **divulgação responsável (Responsible Disclosure)**:

1. **Não abra uma Issue pública** para relatar problemas de segurança.
2. Envie um e-mail diretamente ao mantenedor do projeto com os detalhes técnicos:
   - **Responsável:** Aldair da Silva Azevedo
   - **E-mail:** [aldairazevedo@hotmail.com.br](mailto:aldairazevedo@hotmail.com.br)
   - **Assunto:** `[SECURITY] Vulnerabilidade no projeto energy-demand-forecast`
3. Você também pode utilizar o recurso de **Relatório Privado de Vulnerabilidades** do GitHub:
   - Acesse a aba **Security** > **Advisories** > **Report a vulnerability**.

### Informações Recomendadas no Relatório:
- Descrição clara da vulnerabilidade identificada.
- Passos detalhados para reprodução do comportamento inesperado ou vetor de ataque.
- Componente ou módulo afetado (`src/core`, `src/pipelines`, `src/ui`, dependências).
- Prova de conceito (PoC) ou código de exemplo, se disponível.
- Sugestão de correção ou mitigação temporária, caso possua.

---

## 3. Prazos e Compromisso de Resposta (SLA)

- **Confirmação de recebimento:** Em até **48 horas úteis**.
- **Análise e triagem técnica:** Em até **5 dias úteis**.
- **Lançamento de patch ou mitigação:** Priorizado conforme o nível de severidade (CVSS).
- O crédito pela descoberta será devidamente reconhecido nos lançamentos subsequentes (caso o pesquisador deseje).

---

## 4. Diretrizes de Segurança e Práticas Recomendadas

O projeto adota práticas alinhadas às diretrizes do **OWASP** e políticas de desenvolvimento seguro:

1. **Zero Credenciais no Código:**
   - O repositório não armazena chaves privadas, senhas, tokens de API ou credenciais de banco de dados. Qualquer configuração sensível futura deve ser injetada via variáveis de ambiente (`.env` devidamente listado no `.gitignore`).
2. **Higiene e Integridade dos Dados:**
   - Tratamento estrito de valores corrompidos e sentinelas de sensores (ex.: `-9999`) para prevenir anomalias de execução ou corrupção de memória.
3. **Auditoria de Dependências:**
   - As dependências externas são verificadas periodicamente contra a base de dados de vulnerabilidades conhecidas (CVE/NVD) através de ferramentas como `pip-audit` e GitHub Dependabot.
4. **Execução Segura:**
   - O aplicativo não executa comandos arbitrários no sistema operacional a partir de entradas do usuário.
