import sys
from app.services.db_service import prepare_postgres
from config import Test

sys.path.append("../")
sys.path.append("../../")

prepare_postgres(Test)