--
-- PostgreSQL database dump
--

-- Dumped from database version 16.3
-- Dumped by pg_dump version 16.3

-- Started on 2024-09-09 12:58:45

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 222 (class 1259 OID 16655)
-- Name: Виды_ПО; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Виды_ПО" (
    "код" integer NOT NULL,
    "наименование_ПО" text,
    "вид_ПО" text
);


ALTER TABLE public."Виды_ПО" OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 16654)
-- Name: Виды_ПО_код_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."Виды_ПО_код_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."Виды_ПО_код_seq" OWNER TO postgres;

--
-- TOC entry 4865 (class 0 OID 0)
-- Dependencies: 221
-- Name: Виды_ПО_код_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."Виды_ПО_код_seq" OWNED BY public."Виды_ПО"."код";


--
-- TOC entry 220 (class 1259 OID 16646)
-- Name: Контрагенты; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Контрагенты" (
    "код_контрагента" integer NOT NULL,
    "наименование_контрагента" text,
    "договор" text,
    "примечание" text
);


ALTER TABLE public."Контрагенты" OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 16645)
-- Name: Контрагенты_код_контрагента_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."Контрагенты_код_контрагента_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."Контрагенты_код_контрагента_seq" OWNER TO postgres;

--
-- TOC entry 4866 (class 0 OID 0)
-- Dependencies: 219
-- Name: Контрагенты_код_контрагента_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."Контрагенты_код_контрагента_seq" OWNED BY public."Контрагенты"."код_контрагента";


--
-- TOC entry 215 (class 1259 OID 16506)
-- Name: Справочник_ПО; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Справочник_ПО" (
    "код_ПО" integer NOT NULL,
    "наименование_ПО" text NOT NULL,
    "описание_ПО" text NOT NULL,
    "ссылка_на_сайт_ПО" text NOT NULL,
    "вендор" text,
    "стоимость_за_единицу" integer,
    "признак_ПО" text,
    "примечание" text
);


ALTER TABLE public."Справочник_ПО" OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 16722)
-- Name: Справочник_заказчиков_ПО; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Справочник_заказчиков_ПО" (
    "код_заказчика" integer NOT NULL,
    "заказчик_ПО" text,
    "описание_заказчика" text,
    "ссылка_на_сайт_заказчика" text,
    "примечание" text
);


ALTER TABLE public."Справочник_заказчиков_ПО" OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 16721)
-- Name: Справочник_заказч_код_заказчика_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."Справочник_заказч_код_заказчика_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."Справочник_заказч_код_заказчика_seq" OWNER TO postgres;

--
-- TOC entry 4867 (class 0 OID 0)
-- Dependencies: 229
-- Name: Справочник_заказч_код_заказчика_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."Справочник_заказч_код_заказчика_seq" OWNED BY public."Справочник_заказчиков_ПО"."код_заказчика";


--
-- TOC entry 217 (class 1259 OID 16528)
-- Name: Справочник_лицензий; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Справочник_лицензий" (
    "код_лицензии" integer NOT NULL,
    "наименование_лицензии" text NOT NULL,
    "тип_лицензии" text NOT NULL,
    "счёт_списания" integer,
    "версия_лицензии" integer,
    "примечание" text
);


ALTER TABLE public."Справочник_лицензий" OWNER TO postgres;

--
-- TOC entry 216 (class 1259 OID 16513)
-- Name: Справочник_производителей_ПО; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Справочник_производителей_ПО" (
    "код_производителя" integer NOT NULL,
    "производитель" text NOT NULL,
    "описание_производителя" text NOT NULL,
    "ссылка_на_сайт_производителя" text NOT NULL,
    "примечание" text
);


ALTER TABLE public."Справочник_производителей_ПО" OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 16712)
-- Name: Установка_ПО; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Установка_ПО" (
    "код_установки" integer NOT NULL,
    "наименование_ПО" text,
    "тип_лицензии" text,
    "ФИО" text,
    "отдел" text,
    "ip_адрес" text,
    "наименование_машины" text,
    "чекбокс" boolean,
    "общее_количество" integer,
    "число_установленных_лицензий" integer,
    "дата_установки_ПО" date,
    "чекбокс_условно_бесплатное_ПО" boolean,
    "примечание" text
);


ALTER TABLE public."Установка_ПО" OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 16711)
-- Name: Установка_ПО_код_установки_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."Установка_ПО_код_установки_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."Установка_ПО_код_установки_seq" OWNER TO postgres;

--
-- TOC entry 4868 (class 0 OID 0)
-- Dependencies: 227
-- Name: Установка_ПО_код_установки_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."Установка_ПО_код_установки_seq" OWNED BY public."Установка_ПО"."код_установки";


--
-- TOC entry 218 (class 1259 OID 16573)
-- Name: Учет_лицензий; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Учет_лицензий" (
    "номер_заявки" integer NOT NULL,
    "наименование_ПО" text,
    "тип_лицензии" text,
    "количество_лицензий_ПО" integer,
    "примечание" text
);


ALTER TABLE public."Учет_лицензий" OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 16665)
-- Name: лицензии; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."лицензии" (
    "номер" integer NOT NULL,
    "наименование_ПО" text,
    "контрагент" text,
    "дата_начала_списания" date,
    "дата_окончания_списания" date,
    "счёт_списания" integer,
    "стоимость_ПО" integer,
    "количество" integer,
    "итоговая_стоимость_ПО" integer,
    "признак_ПО" text,
    "страна_производитель" text,
    "срок_действия_лицензии" interval,
    "оплачено" boolean,
    "остаток" double precision,
    "примечание" text,
    "код" text
);


ALTER TABLE public."лицензии" OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 16664)
-- Name: лицензии_номер_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."лицензии_номер_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."лицензии_номер_seq" OWNER TO postgres;

--
-- TOC entry 4869 (class 0 OID 0)
-- Dependencies: 223
-- Name: лицензии_номер_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."лицензии_номер_seq" OWNED BY public."лицензии"."номер";


--
-- TOC entry 226 (class 1259 OID 16685)
-- Name: общая_информация; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."общая_информация" (
    "код_ПО" integer NOT NULL,
    "статья_затрат" text,
    "наименование_ПО_БУ" text,
    "наименование_ПО" text,
    "краткое_наименование_ПО" text,
    "количество" integer,
    "код" text,
    "филиал" text,
    "счет_затрат" double precision,
    "вид_деятельности" text,
    "стоимость_ПО_без_ндс" integer,
    "стоимость_ПО_с_ндс" integer,
    "срок_полезного_использования_мес" integer,
    "дата_начала_списания" date,
    "дата_окончания_списания" date,
    "договор_счет" text,
    "контрагент" text,
    "первичный_документ" text,
    "страна_производитель" text,
    "правообладатель" text,
    "включен_в_реестр" text,
    "срок_предоставления_права" text
);


ALTER TABLE public."общая_информация" OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 16684)
-- Name: общая_информация_код_ПО_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."общая_информация_код_ПО_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."общая_информация_код_ПО_seq" OWNER TO postgres;

--
-- TOC entry 4870 (class 0 OID 0)
-- Dependencies: 225
-- Name: общая_информация_код_ПО_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."общая_информация_код_ПО_seq" OWNED BY public."общая_информация"."код_ПО";


--
-- TOC entry 4676 (class 2604 OID 16658)
-- Name: Виды_ПО код; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Виды_ПО" ALTER COLUMN "код" SET DEFAULT nextval('public."Виды_ПО_код_seq"'::regclass);


--
-- TOC entry 4675 (class 2604 OID 16649)
-- Name: Контрагенты код_контрагента; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Контрагенты" ALTER COLUMN "код_контрагента" SET DEFAULT nextval('public."Контрагенты_код_контрагента_seq"'::regclass);


--
-- TOC entry 4680 (class 2604 OID 16725)
-- Name: Справочник_заказчиков_ПО код_заказчика; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Справочник_заказчиков_ПО" ALTER COLUMN "код_заказчика" SET DEFAULT nextval('public."Справочник_заказч_код_заказчика_seq"'::regclass);


--
-- TOC entry 4679 (class 2604 OID 16715)
-- Name: Установка_ПО код_установки; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Установка_ПО" ALTER COLUMN "код_установки" SET DEFAULT nextval('public."Установка_ПО_код_установки_seq"'::regclass);


--
-- TOC entry 4677 (class 2604 OID 16668)
-- Name: лицензии номер; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."лицензии" ALTER COLUMN "номер" SET DEFAULT nextval('public."лицензии_номер_seq"'::regclass);


--
-- TOC entry 4678 (class 2604 OID 16688)
-- Name: общая_информация код_ПО; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."общая_информация" ALTER COLUMN "код_ПО" SET DEFAULT nextval('public."общая_информация_код_ПО_seq"'::regclass);


--
-- TOC entry 4851 (class 0 OID 16655)
-- Dependencies: 222
-- Data for Name: Виды_ПО; Type: TABLE DATA; Schema: public; Owner: postgres



--
-- TOC entry 4871 (class 0 OID 0)
-- Dependencies: 221
-- Name: Виды_ПО_код_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public."Виды_ПО_код_seq"', 179, true);


--
-- TOC entry 4872 (class 0 OID 0)
-- Dependencies: 219
-- Name: Контрагенты_код_контрагента_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public."Контрагенты_код_контрагента_seq"', 41, true);


--
-- TOC entry 4873 (class 0 OID 0)
-- Dependencies: 229
-- Name: Справочник_заказч_код_заказчика_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public."Справочник_заказч_код_заказчика_seq"', 12, true);


--
-- TOC entry 4874 (class 0 OID 0)
-- Dependencies: 227
-- Name: Установка_ПО_код_установки_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public."Установка_ПО_код_установки_seq"', 1, true);


--
-- TOC entry 4875 (class 0 OID 0)
-- Dependencies: 223
-- Name: лицензии_номер_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public."лицензии_номер_seq"', 157, true);


--
-- TOC entry 4876 (class 0 OID 0)
-- Dependencies: 225
-- Name: общая_информация_код_ПО_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public."общая_информация_код_ПО_seq"', 200, true);


--
-- TOC entry 4692 (class 2606 OID 16662)
-- Name: Виды_ПО Виды_ПО_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Виды_ПО"
    ADD CONSTRAINT "Виды_ПО_pkey" PRIMARY KEY ("код");


--
-- TOC entry 4690 (class 2606 OID 16653)
-- Name: Контрагенты Контрагенты_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Контрагенты"
    ADD CONSTRAINT "Контрагенты_pkey" PRIMARY KEY ("код_контрагента");


--
-- TOC entry 4682 (class 2606 OID 16512)
-- Name: Справочник_ПО Справочник_ПО_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Справочник_ПО"
    ADD CONSTRAINT "Справочник_ПО_pkey" PRIMARY KEY ("код_ПО");


--
-- TOC entry 4700 (class 2606 OID 16729)
-- Name: Справочник_заказчиков_ПО Справочник_заказчиков_ПО_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Справочник_заказчиков_ПО"
    ADD CONSTRAINT "Справочник_заказчиков_ПО_pkey" PRIMARY KEY ("код_заказчика");


--
-- TOC entry 4686 (class 2606 OID 16534)
-- Name: Справочник_лицензий Справочник_лицензий_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Справочник_лицензий"
    ADD CONSTRAINT "Справочник_лицензий_pkey" PRIMARY KEY ("код_лицензии");


--
-- TOC entry 4684 (class 2606 OID 16519)
-- Name: Справочник_производителей_ПО Справочник_производителей_ПО_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Справочник_производителей_ПО"
    ADD CONSTRAINT "Справочник_производителей_ПО_pkey" PRIMARY KEY ("код_производителя");


--
-- TOC entry 4698 (class 2606 OID 16719)
-- Name: Установка_ПО Установка_ПО_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Установка_ПО"
    ADD CONSTRAINT "Установка_ПО_pkey" PRIMARY KEY ("код_установки");


--
-- TOC entry 4688 (class 2606 OID 16579)
-- Name: Учет_лицензий Учет_лицензий_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Учет_лицензий"
    ADD CONSTRAINT "Учет_лицензий_pkey" PRIMARY KEY ("номер_заявки");


--
-- TOC entry 4694 (class 2606 OID 16672)
-- Name: лицензии лицензии_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."лицензии"
    ADD CONSTRAINT "лицензии_pkey" PRIMARY KEY ("номер");


--
-- TOC entry 4696 (class 2606 OID 16692)
-- Name: общая_информация общая_информация_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."общая_информация"
    ADD CONSTRAINT "общая_информация_pkey" PRIMARY KEY ("код_ПО");


-- Completed on 2024-09-09 12:58:46

--
-- PostgreSQL database dump complete
--

