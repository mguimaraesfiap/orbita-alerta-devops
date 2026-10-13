ORBITA ALERTA - EVIDENCIAS REAIS PARA A ENTREGA

Os quadros de evidencia do Word/PDF sao MODELOS e devem ser substituidos por prints reais.

Tire, no minimo, os seguintes prints no MongoDB Compass/mongosh:
1. Banco orbita_alerta_esg mostrando as 5 collections.
2. usuarios: insertMany, find, updateOne, deleteOne e countDocuments = 10.
3. areas_monitoradas: insertMany, find, updateOne, deleteOne e countDocuments = 10.
4. observacoes_ambientais: insertMany, find, updateOne, deleteOne e countDocuments = 10.
5. alertas: insertMany, find, updateOne, deleteOne e countDocuments = 10.
6. ocorrencias_gestao: insertMany, find, updateOne, deleteOne e countDocuments = 10.
7. Consulta de schema flexivel mostrando obs-001, obs-002, obs-003 e obs-004.
8. Resumo final das 5 contagens.

Conexao local no Compass:
mongodb://127.0.0.1:27017

Execucao do arquivo:
mongosh "mongodb://127.0.0.1:27017" --file ".\orbita_alerta_mongodb.js"
