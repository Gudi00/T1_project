#!/bin/bash

echo "📦 Удаляем старые зависимости..."
rm -rf node_modules package-lock.json
npm uninstall tailwindcss postcss autoprefixer @tailwindcss/postcss

echo "📦 Устанавливаем совместимые версии TailwindCSS v3..."
npm install -D tailwindcss@3 postcss@latest autoprefixer@latest

echo "🛠 Переименовываем postcss.config.js → postcss.config.cjs..."
if [ -f postcss.config.js ]; then
  mv postcss.config.js postcss.config.cjs
fi

echo "🛠 Создаём postcss.config.cjs..."
cat > postcss.config.cjs <<'EOF'
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
EOF

echo "🛠 Создаём tailwind.config.js..."
cat > tailwind.config.js <<'EOF'
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#1E3A8A",
        secondary: "#3B82F6",
        accent: "#93C5FD",
        background: "#0F172A"
      },
    },
  },
  plugins: [
    require("@tailwindcss/forms"),
  ],
}
EOF

echo "🎨 Проверяем src/index.css..."
mkdir -p src
cat > src/index.css <<'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Пример кастомных классов */
.btn {
  @apply bg-secondary text-white hover:bg-primary;
}
EOF

echo "🚀 Устанавливаем зависимости..."
npm install

echo "✅ Готово! Запускаем Vite..."
npm run dev
