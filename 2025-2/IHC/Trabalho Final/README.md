# Análise Crítica e Redesign de Interface - Site UFSC.br

## 📋 Sobre o Projeto

Este projeto consiste em uma análise crítica do site institucional da Universidade Federal de Santa Catarina (UFSC), identificando problemas reais de Interação Humano-Computador (IHC) e propondo soluções fundamentadas em princípios teóricos de usabilidade, acessibilidade e design de interfaces.

## 🎯 Objetivos

- Identificar e documentar problemas reais de IHC no site ufsc.br
- Fundamentar cada problema com base nas heurísticas de Nielsen e princípios de IHC
- Desenvolver protótipo mockado demonstrando as correções propostas
- Produzir documentação acadêmica completa em formato ABNT

## 🏗️ Estrutura do Projeto

```
ufsc-ihc-redesign/
├── README.md                    # Este arquivo
├── docs/                        # Documentação da análise
│   ├── analise-problemas.md     # Análise detalhada dos problemas
│   ├── fundamentacao-teorica.md # Referências teóricas
│   └── screenshots/             # Capturas de tela dos problemas
├── pages/                       # Páginas mockadas com correções
├── assets/                      # CSS, JS, imagens
└── index.html                   # Landing page do protótipo
```

## 🔍 Problemas Identificados

1. **Navegação complexa e sobrecarga cognitiva**
2. **Falta de feedback visual em interações**
3. **Hierarquia visual inconsistente**
4. **Problemas de acessibilidade (contraste e navegação)**
5. **Linguagem técnica não adequada ao público-alvo**
6. **Falta de prevenção de erros em formulários**
7. **Consistência visual e de padrões**

## 🛠️ Tecnologias Utilizadas

- HTML5
- CSS3 (com foco em acessibilidade WCAG AA)
- JavaScript (vanilla)
- GitHub Pages (hospedagem)

## 📚 Referências Teóricas

- Nielsen, J. (1994). "10 Usability Heuristics for User Interface Design"
- Norman, D. (2013). "The Design of Everyday Things"
- Preece, J. et al. (2015). "Interaction Design: Beyond Human-Computer Interaction"
- WCAG 2.1 Guidelines

## 📄 Documentação

A documentação completa do projeto está disponível em PDF (formato ABNT) e inclui:
- Análise detalhada de cada problema identificado
- Fundamentação teórica baseada em heurísticas de Nielsen
- Propostas de correção com justificativas
- Screenshots comparativos (antes/depois)

## 🚀 Como Executar

### Método 1: Usando Python (Recomendado) ⭐
1. Certifique-se de ter Python instalado
2. Execute no terminal:
   ```bash
   python main.py
   ```
3. O script irá:
   - Iniciar um servidor HTTP local na porta 8000
   - Abrir automaticamente o navegador
   - Servir todos os arquivos corretamente

### Método 2: Abrir Diretamente
1. Abra o arquivo `index.html` diretamente no navegador
2. **Nota:** Alguns recursos podem não funcionar devido a restrições de segurança

### Método 3: Servidor HTTP do Python
```bash
python -m http.server 8000
```
Depois acesse: `http://localhost:8000`

### GitHub Pages
O projeto será hospedado no GitHub Pages. Acesse: [Link a ser adicionado]

## 📊 Status do Projeto

- ✅ **Fase 1**: Análise crítica e fundamentação teórica - CONCLUÍDA
- ✅ **Fase 2**: Desenvolvimento do protótipo - CONCLUÍDA (100%)
- ⏳ **Fase 3**: Documentação acadêmica em PDF - PENDENTE
- ⏳ **Fase 4**: Revisão final e publicação - PENDENTE

Veja mais detalhes em `PROGRESSO.md`

## 🎨 Design System

O projeto utiliza um design system completo com:
- **Cores**: Paleta baseada nas cores oficiais da UFSC
- **Tipografia**: Roboto (títulos) e Open Sans (corpo)
- **Espaçamentos**: Sistema baseado em múltiplos de 8px
- **Componentes**: Botões, formulários, cards, navegação padronizados
- **Acessibilidade**: Conformidade com WCAG 2.1 nível AA

## ♿ Acessibilidade

O protótipo foi desenvolvido com foco em acessibilidade:
- Contraste adequado (WCAG AA)
- Navegação completa por teclado
- Estrutura semântica HTML5
- Atributos ARIA apropriados
- Skip links para conteúdo principal
- Indicadores de foco visíveis

## 📱 Responsividade

Design mobile-first com breakpoints:
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

## 🔧 Funcionalidades Implementadas

- ✅ Validação de formulários em tempo real
- ✅ Máscaras de entrada (CPF, telefone)
- ✅ Feedback visual em interações
- ✅ Navegação por teclado completa
- ✅ Tooltips explicativos
- ✅ Menu responsivo (hambúrguer para mobile)
- ✅ Breadcrumbs para navegação contextual

## 📚 Referências Bibliográficas

- NIELSEN, Jakob. 10 Usability Heuristics for User Interface Design. Nielsen Norman Group, 1994.
- NORMAN, Donald A. The Design of Everyday Things: Revised and Expanded Edition. New York: Basic Books, 2013.
- PREECE, Jennifer; ROGERS, Yvonne; SHARP, Helen. Interaction Design: Beyond Human-Computer Interaction. 5. ed. Chichester: John Wiley & Sons, 2015.
- WORLD WIDE WEB CONSORTIUM (W3C). Web Content Accessibility Guidelines (WCAG) 2.1. W3C Recommendation, 2018.

## 👥 Autores

Projeto desenvolvido para a disciplina de Interface Humano-Computador (IHC) - UFSC

## 📝 Licença

Este projeto é acadêmico e foi desenvolvido para fins educacionais.

