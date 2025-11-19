# Planejamento do Protótipo - Correções de IHC

## 🎯 Estrutura do Protótipo

### Páginas a Desenvolver

1. **index.html** - Landing page explicativa do projeto
2. **pages/navegacao-melhorada.html** - Correção do Problema 1 (Navegação Complexa)
3. **pages/feedback-visual.html** - Correção do Problema 2 (Feedback Visual)
4. **pages/hierarquia-visual.html** - Correção do Problema 3 (Hierarquia Visual)
5. **pages/acessibilidade.html** - Correção do Problema 4 (Acessibilidade)
6. **pages/linguagem-clara.html** - Correção do Problema 5 (Linguagem Técnica)
7. **pages/formularios.html** - Correção do Problema 6 (Prevenção de Erros)
8. **pages/consistencia.html** - Correção do Problema 7 (Consistência Visual)

## 🎨 Design System

### Cores
- **Primária**: Azul UFSC (#003366)
- **Secundária**: Amarelo UFSC (#FFCC00)
- **Sucesso**: Verde (#28A745)
- **Erro**: Vermelho (#DC3545)
- **Aviso**: Laranja (#FFC107)
- **Texto**: Cinza Escuro (#212529)
- **Fundo**: Branco (#FFFFFF) / Cinza Claro (#F8F9FA)

### Tipografia
- **Títulos**: 'Roboto', sans-serif (bold)
- **Corpo**: 'Open Sans', sans-serif (regular)
- **Tamanhos**: 
  - H1: 2.5rem (40px)
  - H2: 2rem (32px)
  - H3: 1.75rem (28px)
  - H4: 1.5rem (24px)
  - Corpo: 1rem (16px)
  - Pequeno: 0.875rem (14px)

### Espaçamentos
- **Base**: 8px
- **Espaçamentos**: 8px, 16px, 24px, 32px, 48px, 64px

### Componentes
- Botões (primário, secundário, texto)
- Formulários (inputs, selects, checkboxes)
- Cards
- Navegação (menu hambúrguer, breadcrumbs)
- Modais/Tooltips
- Feedback visual (alerts, loading states)

## 📱 Responsividade

- **Mobile First**: Design iniciado para mobile
- **Breakpoints**:
  - Mobile: < 768px
  - Tablet: 768px - 1024px
  - Desktop: > 1024px

## ♿ Acessibilidade

- Contraste mínimo WCAG AA (4.5:1)
- Navegação por teclado completa
- ARIA labels apropriados
- Estrutura semântica HTML5
- Foco visível em todos os elementos interativos

## 🛠️ Tecnologias

- HTML5 semântico
- CSS3 (Grid, Flexbox, Custom Properties)
- JavaScript Vanilla (sem frameworks)
- Dados mockados em JSON

## 📊 Dados Mockados

### Notícias
```json
{
  "noticias": [
    {
      "id": 1,
      "titulo": "UFSC lança novo programa de extensão",
      "data": "2025-11-15",
      "categoria": "Extensão",
      "resumo": "Programa visa aproximar universidade da comunidade..."
    }
  ]
}
```

### Serviços Estudantis
```json
{
  "servicos": [
    {
      "id": 1,
      "nome": "Assistência Estudantil",
      "descricao": "Programas de apoio financeiro e social",
      "link": "/servicos/assistencia-estudantil"
    }
  ]
}
```

### Eventos
```json
{
  "eventos": [
    {
      "id": 1,
      "titulo": "Semana Acadêmica de TIC",
      "data": "2025-12-01",
      "local": "Auditório do CCE"
    }
  ]
}
```

## 🎯 Funcionalidades por Página

### 1. Navegação Melhorada
- Menu hambúrguer para mobile
- Menu principal simplificado (5-7 itens)
- Busca destacada e inteligente
- Breadcrumbs
- Menu de acesso rápido

### 2. Feedback Visual
- Estados hover, focus, active em todos elementos
- Transições suaves
- Indicadores de loading
- Feedback tátil (mobile)

### 3. Hierarquia Visual
- Sistema de tipografia claro
- Grid system consistente
- Contraste e espaçamento adequados
- Elementos importantes destacados

### 4. Acessibilidade
- Contraste WCAG AA
- Navegação por teclado
- ARIA labels
- Modo alto contraste

### 5. Linguagem Clara
- Tooltips explicativos
- Descrições claras
- Glossário acessível
- Linguagem simples

### 6. Formulários
- Validação em tempo real
- Máscaras de entrada
- Mensagens de erro claras
- Autocomplete

### 7. Consistência
- Design system aplicado
- Componentes padronizados
- Padrões visuais consistentes

