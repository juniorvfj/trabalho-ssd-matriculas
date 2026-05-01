"""
Autores: Vicente Jr., Brenno Ribeiro e Rosane
Módulo: Seed (Carga Inicial de Dados)
Descrição: Responsável por popular o banco de dados (geralmente o banco de desenvolvimento
ou testes) com dados estruturais básicos: Cursos, Disciplinas, Alunos, Turmas e 
Pré-requisitos. Facilita a validação manual e automatizada do sistema recém-instanciado.
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text

# Importar modelos e Base
from app.core.database import Base
from app.modules.cursos.infrastructure.orm_models import Curso
from app.modules.disciplinas.infrastructure.orm_models import Disciplina, DisciplinaPrerequisito
from app.modules.alunos.infrastructure.orm_models import Aluno
from app.modules.turmas.infrastructure.orm_models import Turma
from app.modules.historicos.infrastructure.orm_models import HistoricoAcademico, StatusHistorico

# Para usar tanto no banco principal quanto no de teste se necessário
DATABASE_URL = "postgresql+asyncpg://postgres:password@db:5432/matricula_db"

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def seed_data():
    async with SessionLocal() as session:
        # 1. Criar Cursos
        curso_cc = Curso(codigo="BCC", nome="Ciência da Computação")
        curso_mec = Curso(codigo="MEC", nome="Mestrado em Engenharia Elétrica - Cibersegurança")
        session.add_all([curso_cc, curso_mec])
        await session.commit()
        await session.refresh(curso_cc)
        await session.refresh(curso_mec)

        # 2. Criar Disciplinas para CC
        d1 = Disciplina(codigo="MATA01", nome="Algoritmos e Estruturas de Dados I", curso_id=curso_cc.id, carga_horaria=60, creditos=4)
        d2 = Disciplina(codigo="MATA02", nome="Algoritmos e Estruturas de Dados II", curso_id=curso_cc.id, carga_horaria=60, creditos=4)
        d3 = Disciplina(codigo="MATA03", nome="Banco de Dados", curso_id=curso_cc.id, carga_horaria=60, creditos=4)
        
        # 3. Criar Disciplinas para Mestrado
        d4 = Disciplina(codigo="MEC01", nome="Fundamentos de Cibersegurança", curso_id=curso_mec.id, carga_horaria=45, creditos=3)
        d5 = Disciplina(codigo="MEC02", nome="Criptografia Avançada", curso_id=curso_mec.id, carga_horaria=45, creditos=3)
        d6 = Disciplina(codigo="MEC03", nome="Segurança de Sistemas Distribuídos", curso_id=curso_mec.id, carga_horaria=45, creditos=3)

        session.add_all([d1, d2, d3, d4, d5, d6])
        await session.commit()
        await session.refresh(d1)
        await session.refresh(d2)
        await session.refresh(d3)
        await session.refresh(d4)
        await session.refresh(d5)
        await session.refresh(d6)

        # 4. Criar Pré-requisitos
        # d2 precisa de d1
        pr1 = DisciplinaPrerequisito(disciplina_id=d2.id, prerequisito_id=d1.id)
        # d6 precisa de d4 e d5
        pr2 = DisciplinaPrerequisito(disciplina_id=d6.id, prerequisito_id=d4.id)
        pr3 = DisciplinaPrerequisito(disciplina_id=d6.id, prerequisito_id=d5.id)
        session.add_all([pr1, pr2, pr3])
        await session.commit()

        # 5. Criar Alunos
        from datetime import date
        alunos = []
        for i in range(1, 6):
            alunos.append(Aluno(nome=f"Aluno CC {i}", email=f"aluno.cc{i}@ufba.br", matricula=f"11122233{i}", data_admissao=date(2025, 1, 1), curso_id=curso_cc.id, ira=8.5 - (i*0.1)))
        for i in range(1, 6):
            alunos.append(Aluno(nome=f"Aluno Mestrado {i}", email=f"aluno.mec{i}@ufba.br", matricula=f"44455566{i}", data_admissao=date(2025, 1, 1), curso_id=curso_mec.id, ira=9.0 - (i*0.1)))
        
        session.add_all(alunos)
        await session.commit()
        for a in alunos:
            await session.refresh(a)

        # 6. Criar Periodo Letivo
        from app.modules.turmas.infrastructure.orm_models import PeriodoLetivo
        from datetime import date
        periodo = PeriodoLetivo(codigo="2025.1", descricao="Primeiro Semestre de 2025", data_inicio=date(2025, 3, 1), data_fim=date(2025, 7, 15), ativo=False)
        periodo_atual = PeriodoLetivo(codigo="2026.1", descricao="Primeiro Semestre de 2026", data_inicio=date(2026, 3, 1), data_fim=date(2026, 7, 15), ativo=True)
        session.add_all([periodo, periodo_atual])
        await session.commit()
        await session.refresh(periodo)
        await session.refresh(periodo_atual)

        # 7. Criar Histórico (Caminho feliz e caminho de bloqueio)
        # Aluno CC 1 já cursou d1, pode cursar d2
        h1 = HistoricoAcademico(aluno_id=alunos[0].id, disciplina_id=d1.id, periodo_letivo_id=periodo.id, nota_final=9.0, status=StatusHistorico.APROVADO, aprovado=True)
        # Aluno Mestrado 1 já cursou d4 e d5, pode cursar d6
        h2 = HistoricoAcademico(aluno_id=alunos[5].id, disciplina_id=d4.id, periodo_letivo_id=periodo.id, nota_final=8.5, status=StatusHistorico.APROVADO, aprovado=True)
        h3 = HistoricoAcademico(aluno_id=alunos[5].id, disciplina_id=d5.id, periodo_letivo_id=periodo.id, nota_final=8.0, status=StatusHistorico.APROVADO, aprovado=True)
        
        session.add_all([h1, h2, h3])
        await session.commit()

        # 8. Criar Turmas
        t1 = Turma(codigo_turma="T01", disciplina_id=d2.id, horario_serializado="24T34", vagas_totais=30, vagas_ocupadas=0, periodo_letivo_id=periodo_atual.id, ativa=True)
        t2 = Turma(codigo_turma="T02", disciplina_id=d6.id, horario_serializado="35M12", vagas_totais=20, vagas_ocupadas=0, periodo_letivo_id=periodo_atual.id, ativa=True)
        session.add_all([t1, t2])
        await session.commit()

        print("✔ Dados do Seed inseridos com sucesso!")

if __name__ == "__main__":
    asyncio.run(seed_data())
