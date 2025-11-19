# 📁 Pasta da Homepage Corrigida

## Onde colocar os arquivos da nova página da UFSC

Coloque os arquivos da sua nova homepage corrigida nesta pasta seguindo esta estrutura:

```
pages/homepage/
├── index.html          ← HTML principal da homepage corrigida
├── style.css           ← Estilos específicos da homepage (se houver)
└── script.js           ← Scripts específicos da homepage (se houver)
```

## Estrutura Recomendada

### Se você tem apenas HTML:
- Coloque o arquivo HTML como `index.html` nesta pasta

### Se você tem HTML + CSS + JS separados:
- `index.html` - HTML principal
- `style.css` - Estilos específicos (opcional, pode usar apenas o style.css compartilhado)
- `script.js` - Scripts específicos (opcional)

## Links e Referências

Após colocar os arquivos, você pode acessar a homepage em:
- `pages/homepage/` ou `pages/homepage/index.html`

## CSS e JS Compartilhados

Se precisar usar os estilos compartilhados do projeto, use:
- CSS: `../../assets/css/style.css`
- JS: `../../assets/js/main.js`

## Exemplo de Estrutura no HTML

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UFSC - Homepage Corrigida</title>
    
    <!-- CSS Compartilhado -->
    <link rel="stylesheet" href="../../assets/css/style.css">
    
    <!-- CSS Específico (se houver) -->
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <!-- Conteúdo da sua homepage -->
    
    <!-- Scripts Compartilhados -->
    <script src="../../assets/js/main.js"></script>
    
    <!-- Scripts Específicos (se houver) -->
    <script src="script.js"></script>
</body>
</html>
```

