--------------------------------------------------------
--  File created - november-04-2020   
--------------------------------------------------------
-- Run as postgres in database SIGAA 
--CREATE EXTENSION unaccent;

-- Run as SIGAA 

--------------------------------------------------------
--  drop TABLES
--------------------------------------------------------
--drop table SIGAA_MATRICULA_HISTORICO;
--drop table SIGAA_MATRICULA;
--drop table SIGAA_MATRICULA_STATUS;
--drop table SIGAA_RL_ALUNO_CURSO_DISCIPLINA;
--drop table SIGAA_RL_ALUNO_CURSO;
--drop table SIGAA_ALUNO;
--drop table SIGAA_RL_TURMA_HORARIOAULA;
--drop table SIGAA_TURMA;
--drop table SIGAA_TURMA_HORARIOAULA;
--drop table SIGAA_RL_CURRICULO_DISCIPLINA;
--drop table SIGAA_PREREQ;
--drop table SIGAA_RL_CURRICULO_CURSO; 
--drop table SIGAA_CURRICULO;
--drop table SIGAA_DISCIPLINA;
--drop table SIGAA_RL_CURSO_UNIDADE;
--drop table SIGAA_CURSO;
--drop table SIGAA_UNIDADE;


--------------------------------------------------------
--  DDL for Table SIGAA_UNIDADE
--------------------------------------------------------
CREATE TABLE SIGAA_UNIDADE
(
    ID character varying(3) NOT NULL,
    NOME character varying(100) NOT NULL,
    PRIMARY KEY (ID)
);
   
CREATE UNIQUE INDEX PK_SIGAA_UNIDADE ON SIGAA_UNIDADE (ID);

--------------------------------------------------------
--  DDL for Table SIGAA_DISCIPLINA
--------------------------------------------------------
CREATE TABLE SIGAA_DISCIPLINA 
(
	ID character varying(7) NOT NULL, 
    NOME character varying(100), 
    MODALIDADE CHARACTER VARYING(50),
    CARGA_HORARIA_TEORICA numeric(3,0),
    CARGA_HORARIA_PRATICA numeric(3,0),
    UNIDADE character varying(3) NOT NULL, 
    PRIMARY KEY (ID),
    CONSTRAINT FK_UNIDADE FOREIGN KEY (UNIDADE)
        REFERENCES SIGAA_UNIDADE (ID)
);

CREATE UNIQUE INDEX PK_SIGAA_DISCIPLINA ON SIGAA_DISCIPLINA (ID);
  
--------------------------------------------------------
--  DDL for Table SIGAA_PREREQ
--------------------------------------------------------
CREATE TABLE SIGAA_PREREQ 
(
	DISCIPLINA_REQUER character varying(7) NOT NULL,
	DISCIPLINA_REQUERIDO character varying(7) NOT NULL,
    PRIMARY KEY (DISCIPLINA_REQUER, DISCIPLINA_REQUERIDO),
    CONSTRAINT FK_DISCIPLINA_REQUER FOREIGN KEY (DISCIPLINA_REQUER)
        REFERENCES SIGAA_DISCIPLINA (ID),
    CONSTRAINT FK_DISCIPLINA_REQUERIDO FOREIGN KEY (DISCIPLINA_REQUERIDO)
        REFERENCES SIGAA_DISCIPLINA (ID)
);

--------------------------------------------------------
--  DDL for Table SIGAA_CURSO
--------------------------------------------------------
CREATE TABLE SIGAA_CURSO
(
    ID character varying(4) NOT NULL,
    NOME character varying(100) NOT NULL,
	GRAU_ACADEMICO character varying(15) NOT NULL,
	TURNO character varying(10) NOT NULL,
	MODALIDADE character varying(25) NOT NULL,
    COORDENADOR CHARACTER VARYING(100),
    PRIMARY KEY (ID)
);   

CREATE UNIQUE INDEX PK_SIGAA_CURSO ON SIGAA_CURSO (ID);

--------------------------------------------------------
--  DDL for Table SIGAA_RL_CURSO_UNIDADE
--------------------------------------------------------
CREATE TABLE SIGAA_RL_CURSO_UNIDADE
(
    CURSO character varying(4) NOT NULL,
    UNIDADE character varying(3) NOT NULL,
    PRIMARY KEY (CURSO, UNIDADE),
    CONSTRAINT FK_UNIDADE FOREIGN KEY (UNIDADE)
        REFERENCES SIGAA_UNIDADE (ID),
    CONSTRAINT FK_CURSO FOREIGN KEY (CURSO)
        REFERENCES SIGAA_CURSO (ID)
);

--------------------------------------------------------
--  DDL for Table SIGAA_CURRICULO
--------------------------------------------------------
CREATE TABLE SIGAA_CURRICULO
(
    ID character varying(7) NOT NULL,
    STATUS CHARACTER varying(1),
    PERIODO_LETIVO_VIGOR character varying(5) NOT NULL,
    CARGA_HORARIA_MINIMA_TOTAL numeric(5, 0) NOT NULL,
    CARGA_HORARIA_MINIMA_OPT numeric(5, 0) NOT NULL,
    CARGA_HORARIA_OBR numeric(5, 0) NOT NULL,
    CARGA_HORARIA_ELETIVA_MAX numeric(5, 0) NOT NULL,
	CARGA_HORARIA_MAX_PERIODO numeric(5,0) not null,
    NUM_PERIODOS numeric(2, 0) NOT NULL,
    MIN_PERIODOS numeric(2, 0) NOT NULL,
    MAX_PERIODOS numeric(2, 0) NOT NULL,
    PRIMARY KEY (ID)
);   

CREATE UNIQUE INDEX PK_SIGAA_CURRICULO ON SIGAA_CURRICULO (ID);

--------------------------------------------------------
--  DDL for Table SIGAA_RL_CURRICULO_CURSO
--------------------------------------------------------
CREATE TABLE SIGAA_RL_CURRICULO_CURSO
(
    CURRICULO character varying(7) NOT NULL,
    CURSO character varying(4) NOT NULL,
    PRIMARY KEY (CURRICULO,CURSO),
    CONSTRAINT FK_CURSO FOREIGN KEY (CURSO)
        REFERENCES SIGAA_CURSO (ID),
    CONSTRAINT FK_CURRICULO FOREIGN KEY (CURRICULO)
        REFERENCES SIGAA_CURRICULO (ID)
);

--------------------------------------------------------
--  DDL for Table SIGAA_RL_CURRICULO_DISCIPLINA
--------------------------------------------------------
CREATE TABLE SIGAA_RL_CURRICULO_DISCIPLINA
(
    CURRICULO character varying(7) NOT NULL,
	DISCIPLINA character varying(7) NOT NULL,
    PERIODO numeric(2,0),
	TIPO character varying(15) NOT NULL,
    PRIMARY KEY (CURRICULO, DISCIPLINA),
    CONSTRAINT FK_CURRICULO FOREIGN KEY (CURRICULO)
        REFERENCES SIGAA_CURRICULO (ID),
    CONSTRAINT FK_DISCIPLINA FOREIGN KEY (DISCIPLINA)
        REFERENCES SIGAA_DISCIPLINA (ID)
);

--------------------------------------------------------
--  DDL for Table SIGAA_TURMA_HORARIOAULA
--------------------------------------------------------
CREATE TABLE SIGAA_TURMA_HORARIOAULA 
(
	ID character varying(3) NOT NULL,
	DIA character varying(3) NOT NULL,
	HORA_INICIO character varying(5) NOT NULL,
	HORA_FIM character varying(5) NOT NULL,
    PRIMARY KEY (ID), 
	CONSTRAINT HORARIOAULA_UNIQUE UNIQUE (DIA,HORA_INICIO,HORA_FIM)
);

--------------------------------------------------------
--  DML for Table SIGAA_TURMA_HORARIOAULA
--------------------------------------------------------
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (208,'SEG','08:00','09:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (210,'SEG','10:00','11:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (212,'SEG','12:00','13:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (214,'SEG','14:00','15:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (216,'SEG','16:00','17:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (218,'SEG','18:00','19:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (220,'SEG','20:00','21:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (219,'SEG','19:00','20:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (221,'SEG','21:00','22:50');

Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (308,'TER','08:00','09:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (310,'TER','10:00','11:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (312,'TER','12:00','13:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (314,'TER','14:00','15:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (316,'TER','16:00','17:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (318,'TER','18:00','19:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (320,'TER','20:00','21:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (319,'TER','19:00','20:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (321,'TER','21:00','22:50');

Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (408,'QUA','08:00','09:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (410,'QUA','10:00','11:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (412,'QUA','12:00','13:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (414,'QUA','14:00','15:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (416,'QUA','16:00','17:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (418,'QUA','18:00','19:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (420,'QUA','20:00','21:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (419,'QUA','19:00','20:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (421,'QUA','21:00','22:50');

Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (508,'QUI','08:00','09:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (510,'QUI','10:00','11:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (512,'QUI','12:00','13:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (514,'QUI','14:00','15:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (516,'QUI','16:00','17:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (518,'QUI','18:00','19:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (520,'QUI','20:00','21:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (519,'QUI','19:00','20:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (521,'QUI','21:00','22:50');

Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (608,'SEX','08:00','09:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (610,'SEX','10:00','11:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (612,'SEX','12:00','13:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (614,'SEX','14:00','15:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (616,'SEX','16:00','17:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (618,'SEX','18:00','19:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (620,'SEX','20:00','21:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (619,'SEX','19:00','20:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (621,'SEX','21:00','22:50');

Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (708,'SAB','08:00','09:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (710,'SAB','10:00','15:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (712,'SAB','12:00','13:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (714,'SAB','14:00','15:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (716,'SAB','16:00','17:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (718,'SAB','18:00','19:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (720,'SAB','20:00','21:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (719,'SAB','19:00','20:50');
Insert into SIGAA_TURMA_HORARIOAULA (ID,DIA,HORA_INICIO,HORA_FIM)  values (721,'SAB','21:00','22:50');

--------------------------------------------------------
--  DDL for Table SIGAA_TURMA
--------------------------------------------------------
CREATE TABLE SIGAA_TURMA 
(
    ID serial,
	CODIGO character varying(2) NOT NULL,
    PERIODO_LETIVO character varying(5) NOT NULL,
	DISCIPLINA character varying(7) NOT NULL,
	VAGAS NUMERIC(3,0),
    SEDE CHARACTER VARYING(50),
    PRIMARY KEY (ID),
    CONSTRAINT TURMA_UNIQUE UNIQUE (CODIGO, PERIODO_LETIVO,DISCIPLINA),
    CONSTRAINT FK_DISCIPLINA FOREIGN KEY (DISCIPLINA)
        REFERENCES SIGAA_DISCIPLINA (ID)
);

CREATE UNIQUE INDEX PK_SIGAA_TURMA ON SIGAA_TURMA (ID);

--------------------------------------------------------
--  DDL for Table SIGAA_RL_TURMA_HORARIOAULA
--------------------------------------------------------
CREATE TABLE SIGAA_RL_TURMA_HORARIOAULA 
(
	TURMA INTEGER,
	HORARIOAULA character varying(2), 
    PRIMARY KEY (TURMA,HORARIOAULA), 
	CONSTRAINT TURMA_HAULA_UNIQUE UNIQUE (HORARIOAULA,TURMA),
    CONSTRAINT FK_HORARIOAULA FOREIGN KEY (HORARIOAULA)
        REFERENCES SIGAA_TURMA_HORARIOAULA (ID),
    CONSTRAINT FK_TURMA FOREIGN KEY (TURMA)
        REFERENCES SIGAA_TURMA (ID)
);

--------------------------------------------------------
--  DDL for Table SIGAA_ALUNO
--------------------------------------------------------
CREATE TABLE SIGAA_ALUNO 
(
	MATRICULA character varying(9) NOT NULL,
    NOME character varying(80) NOT NULL, 
    PRIMARY KEY (MATRICULA) 
);

CREATE UNIQUE INDEX PK_SIGAA_ALUNO ON SIGAA_ALUNO (MATRICULA);

--------------------------------------------------------
--  DDL for Table SIGAA_RL_ALUNO_CURSO
--------------------------------------------------------
CREATE TABLE SIGAA_RL_ALUNO_CURSO 
(
	ID serial,
	ALUNO character varying(9) NOT NULL,
    CURSO character varying(4) NOT NULL,
    CURRICULO CHARACTER VARYING(7) NOT NULL,
    DATA_REGISTRO DATE NOT NULL, 
    PERIODO_LETIVO_REGISTRO character varying(5) NOT NULL,
    STATUS character varying(1),
	IRA REAL,
    PRIMARY KEY(ID), 
	CONSTRAINT ALUNO_CURSO_UNIQUE UNIQUE (ALUNO,CURSO,PERIODO_LETIVO_REGISTRO),
    CONSTRAINT FK_ALUNO FOREIGN KEY (ALUNO)
        REFERENCES SIGAA_ALUNO (MATRICULA),
    CONSTRAINT FK_CURSO FOREIGN KEY (CURSO)
        REFERENCES SIGAA_CURSO (ID),
    CONSTRAINT FK_CURRICULO FOREIGN KEY (CURRICULO)
        REFERENCES SIGAA_CURRICULO (ID)
);


--------------------------------------------------------
--  DDL for Table SIGAA_RL_ALUNO_CURSO_DISCIPLINA
--------------------------------------------------------
CREATE TABLE SIGAA_RL_ALUNO_CURSO_DISCIPLINA
(
	ALUNO_CURSO integer NOT NULL,
	DISCIPLINA character varying(7) NOT NULL,
    PERIODO_LETIVO character varying(5) NOT NULL,
    MENCAO character varying(2),
    PRIMARY KEY (ALUNO_CURSO, DISCIPLINA,PERIODO_LETIVO),
    CONSTRAINT FK_ALUNO_CURSO FOREIGN KEY (ALUNO_CURSO)
        REFERENCES SIGAA_RL_ALUNO_CURSO (ID),
    CONSTRAINT FK_DISCIPLINA FOREIGN KEY (DISCIPLINA)
        REFERENCES SIGAA_DISCIPLINA (ID)
);

--------------------------------------------------------
--  DDL for Table SIGAA_MATRICULA_STATUS
--------------------------------------------------------
CREATE TABLE SIGAA_MATRICULA_STATUS
(
	ID character varying(3) NOT NULL,
	STATUS character varying(30) NOT NULL,
    PRIMARY KEY(ID)
);

--------------------------------------------------------
--  DML for Table SIGAA_MATRICULA_STATUS
--------------------------------------------------------
Insert into SIGAA_MATRICULA_STATUS (ID,STATUS) values 
            ('PRE','Pré-matrícula');
Insert into SIGAA_MATRICULA_STATUS (ID,STATUS) values 
            ('PND','Pedido');
Insert into SIGAA_MATRICULA_STATUS (ID,STATUS) values 
            ('REJ','Retirado');
Insert into SIGAA_MATRICULA_STATUS (ID,STATUS) values 
            ('REA','Retirado pelo aluno');
Insert into SIGAA_MATRICULA_STATUS (ID,STATUS) values 
            ('REC','Retirado pelo coordenador');
Insert into SIGAA_MATRICULA_STATUS (ID,STATUS) values 
            ('MAT','Matriculado');
Insert into SIGAA_MATRICULA_STATUS (ID,STATUS) values 
            ('TRA','Trancamento');
Insert into SIGAA_MATRICULA_STATUS (ID,STATUS) values 
            ('CAN','Cancelado');
Insert into SIGAA_MATRICULA_STATUS (ID,STATUS) values 
            ('NEL','Não elegível');
Insert into SIGAA_MATRICULA_STATUS (ID,STATUS) values 
            ('CEX','Créditos excedidos');
Insert into SIGAA_MATRICULA_STATUS (ID,STATUS) values 
            ('JMD','Já matricula na disciplina');
Insert into SIGAA_MATRICULA_STATUS (ID,STATUS) values 
            ('CON','Conflito de horário');
Insert into SIGAA_MATRICULA_STATUS (ID,STATUS) values 
            ('FUL','Vagas excedidas');
Insert into SIGAA_MATRICULA_STATUS (ID,STATUS) values 
            ('CFM','Confirmado');

--------------------------------------------------------
--  DDL for Table SIGAA_MATRICULA
--------------------------------------------------------
CREATE TABLE SIGAA_MATRICULA
(
   	ID serial, 
	ALUNO_CURSO integer NOT NULL,
    TURMA integer NOT NULL, 
    STATUS character varying(3) NOT NULL,
    PRIORIDADE NUMERIC(2,0) default null,
	PRIMARY KEY (ID),
    CONSTRAINT FK_ALUNO_CURSO FOREIGN KEY (ALUNO_CURSO)
        REFERENCES SIGAA_RL_ALUNO_CURSO (ID),
    CONSTRAINT FK_TURMA FOREIGN KEY (TURMA)
        REFERENCES SIGAA_TURMA (ID),
    CONSTRAINT FK_MATRICULA_STATUS FOREIGN KEY (STATUS)
        REFERENCES SIGAA_MATRICULA_STATUS (ID)
); 

CREATE UNIQUE INDEX PK_SIGAA_MATRICULA ON SIGAA_MATRICULA (ID);

--------------------------------------------------------
--  DDL for Table SIGAA_MATRICULA_HISTORICO
--------------------------------------------------------
CREATE TABLE SIGAA_MATRICULA_HISTORICO
(
   	ID serial, 
	ALUNO_CURSO integer NOT NULL,
    STATUS character varying(3) NOT NULL,
    TURMA integer NOT NULL, 
    PRIORIDADE NUMERIC(2,0) default null,
	DATA_HORA timestamp with time zone,
	PRIMARY KEY (ID),
    CONSTRAINT FK_ALUNO_CURSO FOREIGN KEY (ALUNO_CURSO)
        REFERENCES SIGAA_RL_ALUNO_CURSO (ID),
    CONSTRAINT FK_MATRICULA_STATUS FOREIGN KEY (STATUS)
        REFERENCES SIGAA_MATRICULA_STATUS (ID)
); 

CREATE UNIQUE INDEX PK_SIGAA_MATRICULA_HISTORICO ON SIGAA_MATRICULA_HISTORICO (ID);