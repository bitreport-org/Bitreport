# -*- coding: utf-8 -*-
from app.api import create_app

app = create_app()
app.run(debug=True, port=80, host='0.0.0.0')
