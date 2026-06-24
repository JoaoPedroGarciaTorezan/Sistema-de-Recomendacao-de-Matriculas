class Disciplina:

    def __init__(self, codigo, nome, carga_horaria):
        self.codigo = codigo
        self.nome = nome
        self.carga_horaria = carga_horaria
        self.pre_requisitos = []
        self.estado = "NAO_CURSADA"


    def adicionar_pre_requisito(self, disciplina):
        self.pre_requisitos.append(disciplina)


    def __str__(self):
        return f"{self.codigo} - {self.nome}"