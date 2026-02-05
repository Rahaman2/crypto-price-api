module.exports = {
  apps: [
    {
      name: "crypto-price-api",
      script: "venv/bin/uvicorn",
      args: "app.main:app --host 127.0.0.1 --port 10004",
      cwd: "/var/www/crypto-price-api",
      interpreter: "none",
      autorestart: true,
      watch: false,
      max_memory_restart: "500M",
      env: {
        NODE_ENV: "production",
      },
    },
  ],
};
