from app import app

app.run(host= '0.0.0.0', port=5010, ssl_context=('atopa.crt', 'atopa.key'))