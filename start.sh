#!/bin/bash
# pharmaMS - Script de inicializacao
set -e

echo "=== pharmaMS - Sistema de Gestao Farmaceutica ==="

VENV_DIR="$(dirname "$0")/.venv"

# Criar virtual environment se nao existir
if [ ! -d "$VENV_DIR" ]; then
    echo "[INFO] Criando virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo "[OK] Virtual environment criado em $VENV_DIR"
fi

# Ativar virtual environment
echo "[INFO] Ativando virtual environment..."
source "$VENV_DIR/bin/activate"

# Verificar se .env existe
if [ ! -f .env ]; then
    echo "[INFO] Arquivo .env nao encontrado. Copiando de .env.example..."
    cp .env.example .env
    echo "[INFO] Edite o arquivo .env com as configuracoes corretas."
fi

# Carregar variaveis de ambiente
export $(grep -v '^#' .env | xargs)

# Verificar PostgreSQL
echo "[INFO] Verificando PostgreSQL..."
if command -v pg_isready &> /dev/null; then
    if pg_isready -h ${DB_HOST:-localhost} -p ${DB_PORT:-5433} -q 2>/dev/null; then
        echo "[OK] PostgreSQL esta online na porta ${DB_PORT:-5433}"
    else
        echo "[WARN] PostgreSQL offline. Tentando iniciar..."
        if [ -f start_db.sh ]; then
            bash start_db.sh
            sleep 2
        fi
    fi
else
    echo "[WARN] pg_isready nao encontrado. Verifique o PostgreSQL manualmente."
fi

# Criar banco de dados se nao existir
echo "[INFO] Verificando banco de dados..."
DB_NAME=${DB_NAME:-pharmams}
DB_USER=${DB_USER:-pharmams}
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5433}

if command -v psql &> /dev/null; then
    PGPASSWORD=${DB_PASSWORD:-pharmams123} psql -h $DB_HOST -p $DB_PORT -U $DB_USER -tc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1 || \
        PGPASSWORD=${DB_PASSWORD:-pharmams123} psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "CREATE DATABASE $DB_NAME" 2>/dev/null || true
fi

# Instalar dependencias
echo "[INFO] Instalando dependencias..."
pip install -r requirements.txt --quiet

# Executar migrations
echo "[INFO] Executando migrations..."
python manage.py makemigrations --noinput 2>/dev/null || true
python manage.py migrate --noinput

# Criar superusuario se nao existir
echo "[INFO] Verificando superusuario..."
python manage.py shell -c "
from usuarios.models import Usuario
if not Usuario.objects.filter(is_superuser=True).exists():
    Usuario.objects.create_superuser(
        username='admin',
        email='admin@pharmams.com',
        password='admin123',
        nome_completo='Administrador',
        perfil='admin_master'
    )
    print('[OK] Superusuario criado: admin / admin123')
else:
    print('[OK] Superusuario ja existe')
" 2>/dev/null || true

# Collectstatic
echo "[INFO] Coleteando arquivos estaticos..."
python manage.py collectstatic --noinput 2>/dev/null || true

# Criar diretorios necessarios
mkdir -p media logs staticfiles

echo ""
echo "=== pharmaMS pronto! ==="
echo ""
echo "Para iniciar o servidor:"
echo "  source .venv/bin/activate"
echo "  python manage.py runserver 0.0.0.0:8000"
echo ""
echo "Ou com gunicorn (producao):"
echo "  source .venv/bin/activate"
echo "  gunicorn pharmams.wsgi:application --bind 0.0.0.0:8000 --workers 4"
echo ""
echo "Admin: http://localhost:8000/admin/"
echo "Login: admin / admin123"
