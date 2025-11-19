# Análise Crítica dos Problemas de IHC no Site UFSC.br

## 📊 Metodologia de Análise

A análise foi realizada através de:
- Navegação sistemática do site ufsc.br
- Aplicação das 10 Heurísticas de Usabilidade de Nielsen
- Avaliação de acessibilidade baseada em WCAG 2.1
- Análise comparativa com sites de outras universidades federais
- Consideração do público-alvo diversificado (estudantes, servidores, comunidade externa)

---

## 🔴 Problema 1: Navegação Complexa e Sobrecarga Cognitiva

### Descrição do Problema
O menu principal do site apresenta uma estrutura hierárquica excessivamente complexa, com múltiplos níveis de navegação e uma quantidade massiva de opções simultâneas. O menu possui mais de 50 links diretos visíveis, organizados em categorias que não seguem uma lógica intuitiva para o usuário comum.

### Onde Ocorre
- Menu principal (topo da página)
- Menu de navegação secundário
- Rodapé com múltiplas seções

### Impacto na Experiência do Usuário
- **Sobrecarga cognitiva**: Usuários ficam paralisados pela quantidade de opções
- **Dificuldade de localização**: Informações importantes ficam "perdidas" na massa de links
- **Frustração**: Usuários precisam fazer múltiplos cliques para encontrar o que procuram
- **Abandono**: Usuários podem desistir de encontrar informações específicas

### Públicos Mais Afetados
- **Calouros**: Não conhecem a estrutura organizacional da universidade
- **Comunidade externa**: Não estão familiarizados com a terminologia acadêmica
- **Usuários mobile**: A complexidade é amplificada em telas menores

### Heurísticas Violadas
1. **Heurística #6 - Reconhecimento em vez de recordação**: Usuários precisam "lembrar" onde estão informações específicas
2. **Heurística #8 - Estética e design minimalista**: Interface sobrecarregada com informações
3. **Heurística #3 - Controle e liberdade do usuário**: Usuários se sentem perdidos na navegação

### Fundamentação Teórica
Conforme Nielsen (1994), interfaces devem minimizar a carga cognitiva do usuário, apresentando informações de forma clara e hierárquica. Norman (2013) enfatiza que a navegação deve seguir modelos mentais intuitivos, evitando estruturas que exijam conhecimento prévio do sistema.

### Proposta de Correção
- Implementar menu hambúrguer para mobile
- Reduzir opções visíveis no menu principal (máximo 5-7 itens principais)
- Criar sistema de busca inteligente e destacado
- Implementar breadcrumbs para navegação contextual
- Adicionar menu de "Acesso Rápido" com links mais utilizados

---

## 🔴 Problema 2: Falta de Feedback Visual em Interações

### Descrição do Problema
Muitos elementos interativos do site não fornecem feedback visual claro quando o usuário interage com eles. Botões não mudam de estado ao passar o mouse, links não indicam claramente que são clicáveis, e ações do usuário não geram confirmação visual imediata.

### Onde Ocorre
- Links do menu principal
- Botões de ação
- Formulários de busca
- Links de notícias e eventos

### Impacto na Experiência do Usuário
- **Incerteza**: Usuários não sabem se clicaram corretamente ou se o sistema está processando
- **Frustração**: Múltiplos cliques desnecessários em elementos que não respondem visualmente
- **Acessibilidade**: Usuários com deficiência visual têm dificuldade em identificar elementos interativos
- **Eficiência reduzida**: Usuários perdem tempo tentando entender o estado do sistema

### Públicos Mais Afetados
- **Usuários inexperientes**: Não estão acostumados com interfaces web
- **Usuários com deficiência visual**: Dependem de feedback claro
- **Usuários mobile**: Tela touch requer feedback tátil/visual mais evidente

### Heurísticas Violadas
1. **Heurística #1 - Visibilidade do status do sistema**: Sistema não comunica claramente seu estado
2. **Heurística #4 - Consistência e padrões**: Elementos interativos não seguem padrões visuais consistentes
3. **Heurística #7 - Flexibilidade e eficiência de uso**: Falta de affordances claros reduz eficiência

### Fundamentação Teórica
Nielsen (1994) destaca que o sistema deve sempre informar ao usuário o que está acontecendo através de feedback apropriado. Norman (2013) enfatiza a importância de affordances visuais claras que indiquem como os elementos podem ser manipulados.

### Proposta de Correção
- Implementar estados hover, focus e active em todos os elementos interativos
- Adicionar transições suaves para feedback visual
- Melhorar contraste de links não visitados vs visitados
- Adicionar indicadores de loading para ações que demoram
- Implementar feedback tátil em dispositivos touch

---

## 🔴 Problema 3: Hierarquia Visual Inconsistente

### Descrição do Problema
A página inicial apresenta múltiplos elementos competindo pela atenção do usuário sem uma hierarquia visual clara. Títulos, textos, imagens e call-to-actions têm pesos visuais similares, dificultando a compreensão do que é mais importante.

### Onde Ocorre
- Página inicial (homepage)
- Páginas de seções específicas
- Listagens de notícias e eventos

### Impacto na Experiência do Usuário
- **Confusão visual**: Usuários não sabem onde focar a atenção
- **Tempo de leitura aumentado**: Informações importantes não são encontradas rapidamente
- **Fadiga visual**: Múltiplos elementos competindo causam cansaço
- **Perda de informações importantes**: Conteúdo relevante pode passar despercebido

### Públicos Mais Afetados
- **Usuários com baixa literacia digital**: Têm dificuldade em processar informações complexas
- **Usuários idosos**: Podem ter dificuldade em focar em elementos específicos
- **Usuários em dispositivos móveis**: Hierarquia visual é ainda mais crítica em telas pequenas

### Heurísticas Violadas
1. **Heurística #8 - Estética e design minimalista**: Interface não prioriza informações essenciais
2. **Heurística #6 - Reconhecimento em vez de recordação**: Falta de padrões visuais claros
3. **Heurística #4 - Consistência e padrões**: Hierarquia não é aplicada consistentemente

### Fundamentação Teórica
Preece et al. (2015) destacam que a hierarquia visual é fundamental para guiar a atenção do usuário e facilitar a compreensão. O uso adequado de tipografia, espaçamento e contraste cria uma "arquitetura visual" que orienta o usuário.

### Proposta de Correção
- Estabelecer sistema de tipografia claro (títulos H1-H6 com tamanhos distintos)
- Implementar grid system consistente para organização
- Usar contraste e espaçamento para criar hierarquia
- Destacar elementos importantes (call-to-actions) com cores e tamanhos apropriados
- Reduzir ruído visual removendo elementos desnecessários

---

## 🔴 Problema 4: Problemas de Acessibilidade (Contraste e Navegação)

### Descrição do Problema
O site apresenta problemas de acessibilidade que dificultam o uso por pessoas com deficiência. Alguns textos têm contraste insuficiente com o fundo, elementos não são navegáveis via teclado, e falta estrutura semântica adequada para leitores de tela.

### Onde Ocorre
- Textos em cinza claro sobre fundo branco
- Links sem indicadores de foco visível
- Falta de labels adequados em formulários
- Estrutura HTML sem landmarks ARIA apropriados

### Impacto na Experiência do Usuário
- **Exclusão**: Usuários com deficiência visual não conseguem usar o site adequadamente
- **Conformidade legal**: Site pode não estar em conformidade com leis de acessibilidade
- **Usabilidade geral reduzida**: Problemas de acessibilidade afetam todos os usuários
- **Frustração**: Usuários que dependem de navegação por teclado ficam presos

### Públicos Mais Afetados
- **Usuários com deficiência visual**: Dependem de contraste adequado e leitores de tela
- **Usuários com deficiência motora**: Dependem de navegação por teclado
- **Usuários idosos**: Podem ter dificuldades visuais que são agravadas por baixo contraste

### Heurísticas Violadas
1. **Heurística #1 - Visibilidade do status do sistema**: Elementos não são visíveis para todos os usuários
2. **Heurística #7 - Flexibilidade e eficiência de uso**: Falta de alternativas de acesso
3. **Princípios WCAG**: Violação de critérios de contraste (1.4.3) e navegação por teclado (2.1.1)

### Fundamentação Teórica
As WCAG 2.1 estabelecem que textos devem ter contraste mínimo de 4.5:1 para texto normal e 3:1 para texto grande. Nielsen (1994) enfatiza que sistemas devem ser acessíveis a todos os usuários, independentemente de suas capacidades.

### Proposta de Correção
- Aumentar contraste de todos os textos para atender WCAG AA (mínimo 4.5:1)
- Implementar navegação por teclado completa com indicadores de foco visíveis
- Adicionar landmarks ARIA e estrutura semântica adequada
- Incluir labels descritivos em todos os formulários
- Implementar modo de alto contraste como opção

---

## 🔴 Problema 5: Linguagem Técnica Não Adequada ao Público-Alvo

### Descrição do Problema
O site utiliza terminologia técnica e jargão acadêmico sem explicações adequadas, assumindo que todos os usuários estão familiarizados com a estrutura organizacional da universidade. Termos como "PROEX", "PROGRAD", "CAGR" aparecem sem contexto.

### Onde Ocorre
- Menu de navegação
- Páginas de serviços
- Formulários e documentos
- Links e descrições

### Impacto na Experiência do Usuário
- **Barreira de compreensão**: Usuários não entendem o que cada seção oferece
- **Frustração**: Necessidade de pesquisar termos para entender o site
- **Exclusão**: Usuários menos familiarizados com ambiente acadêmico se sentem excluídos
- **Ineficiência**: Múltiplos cliques para descobrir o significado de termos

### Públicos Mais Afetados
- **Calouros**: Não conhecem a estrutura organizacional da UFSC
- **Comunidade externa**: Não estão familiarizados com siglas acadêmicas
- **Estudantes de outros cursos**: Podem não conhecer siglas específicas de outras áreas

### Heurísticas Violadas
1. **Heurística #2 - Compatibilidade com o mundo real**: Linguagem não corresponde ao conhecimento do usuário
2. **Heurística #6 - Reconhecimento em vez de recordação**: Usuários precisam "lembrar" o que cada sigla significa
3. **Heurística #10 - Ajuda e documentação**: Falta de explicações contextuais

### Fundamentação Teórica
Norman (2013) enfatiza que sistemas devem usar linguagem familiar ao usuário, seguindo convenções do mundo real. Nielsen (1994) destaca que informações devem aparecer em ordem natural e lógica para o usuário.

### Proposta de Correção
- Substituir siglas por nomes completos ou adicionar descrições explicativas
- Implementar tooltips explicativos ao passar o mouse sobre termos técnicos
- Adicionar glossário acessível do site
- Usar linguagem clara e direta, evitando jargão desnecessário
- Criar seção "Para Iniciantes" com explicações simples

---

## 🔴 Problema 6: Falta de Prevenção de Erros em Formulários

### Descrição do Problema
Formulários do site não possuem validação em tempo real, mensagens de erro claras, ou prevenção de erros comuns. Usuários só descobrem problemas após submeter o formulário, e mensagens de erro não são suficientemente descritivas.

### Onde Ocorre
- Formulários de contato
- Busca avançada
- Inscrições em eventos
- Acesso a sistemas

### Impacto na Experiência do Usuário
- **Frustração**: Usuários precisam refazer formulários inteiros após descobrir erros
- **Perda de tempo**: Validação apenas no final do processo
- **Abandono**: Usuários podem desistir de preencher formulários longos
- **Confusão**: Mensagens de erro não explicam claramente como corrigir

### Públicos Mais Afetados
- **Usuários inexperientes**: Não estão familiarizados com formatos esperados
- **Usuários com deficiência cognitiva**: Têm dificuldade em entender mensagens de erro
- **Usuários mobile**: Erros de digitação são mais comuns em telas touch

### Heurísticas Violadas
1. **Heurística #5 - Prevenção de erros**: Sistema não previne erros antes que ocorram
2. **Heurística #9 - Ajudar usuários a reconhecer, diagnosticar e recuperar erros**: Mensagens de erro não são claras
3. **Heurística #1 - Visibilidade do status do sistema**: Validação não é visível durante o preenchimento

### Fundamentação Teórica
Nielsen (1994) destaca que é melhor prevenir erros do que depender de mensagens de erro. Validação em tempo real e feedback imediato reduzem frustração e aumentam eficiência. Preece et al. (2015) enfatizam a importância de mensagens de erro construtivas que guiem o usuário.

### Proposta de Correção
- Implementar validação em tempo real com feedback imediato
- Adicionar máscaras de entrada para campos específicos (CPF, telefone, etc.)
- Criar mensagens de erro descritivas e acionáveis
- Adicionar exemplos de formato esperado nos campos
- Implementar autocomplete para campos comuns

---

## 🔴 Problema 7: Consistência Visual e de Padrões

### Descrição do Problema
O site apresenta inconsistências visuais entre diferentes páginas e seções. Botões têm estilos diferentes, espaçamentos variam, cores não seguem um padrão consistente, e elementos similares se comportam de forma diferente em contextos distintos.

### Onde Ocorre
- Entre páginas de diferentes seções
- Botões e elementos interativos
- Formulários em diferentes contextos
- Navegação secundária

### Impacto na Experiência do Usuário
- **Confusão**: Usuários não sabem o que esperar de elementos similares
- **Curva de aprendizado aumentada**: Cada página parece um novo sistema
- **Frustração**: Comportamentos inesperados quebram expectativas
- **Percepção de qualidade reduzida**: Inconsistência transmite falta de cuidado

### Públicos Mais Afetados
- **Usuários novos**: Não têm conhecimento prévio para compensar inconsistências
- **Usuários com deficiência cognitiva**: Dependem de padrões consistentes
- **Todos os usuários**: Inconsistência afeta eficiência de uso

### Heurísticas Violadas
1. **Heurística #4 - Consistência e padrões**: Interface não segue padrões consistentes
2. **Heurística #6 - Reconhecimento em vez de recordação**: Falta de padrões dificulta reconhecimento
3. **Heurística #3 - Controle e liberdade do usuário**: Inconsistência reduz sensação de controle

### Fundamentação Teórica
Nielsen (1994) enfatiza que usuários não devem se perguntar se palavras, situações ou ações diferentes significam a mesma coisa. Consistência reduz carga cognitiva e aumenta eficiência. Norman (2013) destaca que padrões consistentes criam affordances previsíveis.

### Proposta de Correção
- Criar design system unificado (cores, tipografia, espaçamentos)
- Padronizar componentes reutilizáveis (botões, formulários, cards)
- Documentar padrões de design para manutenção futura
- Implementar componentes consistentes em todas as páginas
- Estabelecer guia de estilo visual para o site

---

## 📊 Resumo dos Problemas Identificados

| # | Problema | Heurística Principal | Gravidade | Impacto |
|---|----------|---------------------|-----------|---------|
| 1 | Navegação Complexa | #6, #8 | Alta | Alto |
| 2 | Falta de Feedback Visual | #1, #4 | Média | Alto |
| 3 | Hierarquia Visual Inconsistente | #8, #6 | Média | Médio |
| 4 | Problemas de Acessibilidade | #1, WCAG | Alta | Crítico |
| 5 | Linguagem Técnica | #2, #6 | Média | Médio |
| 6 | Falta de Prevenção de Erros | #5, #9 | Média | Médio |
| 7 | Inconsistência Visual | #4, #6 | Média | Médio |

---

## 📚 Próximos Passos

1. Coletar screenshots detalhados de cada problema
2. Desenvolver fundamentação teórica mais profunda
3. Criar protótipos das correções propostas
4. Documentar análise completa em formato acadêmico

