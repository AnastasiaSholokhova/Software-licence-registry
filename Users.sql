--
-- PostgreSQL database dump
--

-- Dumped from database version 16.3
-- Dumped by pg_dump version 16.3

-- Started on 2024-07-16 14:47:49

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
-- TOC entry 217 (class 1259 OID 16544)
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    id integer NOT NULL,
    role text
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 16551)
-- Name: user_roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_roles (
    user_id integer,
    role_id integer
);


ALTER TABLE public.user_roles OWNER TO postgres;

--
-- TOC entry 216 (class 1259 OID 16495)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    fullname character varying(100) NOT NULL,
    username character varying(50) NOT NULL,
    password character varying(255) NOT NULL,
    email character varying(50) NOT NULL,
    role text,
    phone_number text
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 215 (class 1259 OID 16494)
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- TOC entry 4801 (class 0 OID 0)
-- Dependencies: 215
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- TOC entry 4642 (class 2604 OID 16498)
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- TOC entry 4794 (class 0 OID 16544)
-- Dependencies: 217
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roles (id, role) FROM stdin;
\.


--
-- TOC entry 4795 (class 0 OID 16551)
-- Dependencies: 218
-- Data for Name: user_roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_roles (user_id, role_id) FROM stdin;
\.


--
-- TOC entry 4793 (class 0 OID 16495)
-- Dependencies: 216
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, fullname, username, password, email, role, phone_number) FROM stdin;
21	Anastasia	Anastasia_Sholokhova	scrypt:32768:8:1$iQl7EMaLKraXILea$8b2e4585875da64e91d84e66289d3b9b43c182afff0683822cd24c8529975a55f362092d544dfc555c2b29f2707f65653375640efa3118368ed3d5caae5337e0	sholokhova.nastia@bk.ru	admin	\N
23	User	User	scrypt:32768:8:1$HI6v3SL3hvXxzG70$860aaf48f555366512c532e64295b8aa42f66e56e9816f11c929778f32e98aaeab511f3bbb77fba24c680e89ac0615aaa61cbc159a323c3518a249cdef357162	irina101@bk.ru	editor	+79167574938
14	someone	someone	scrypt:32768:8:1$LlEzkgeS9wHcZ4ZQ$40af807a997de58d78151f02aa9e0fc59da98e9fb65d51493e624fe2284925e4a5d38d7b10fa7455e6e457d32b8311594c95bd84061ea38c9a6b20b0710256fc	Analstasia.Sholokhova@yandex.ru	editor	\N
20	s1	s1	scrypt:32768:8:1$D2j2i7XDq0VpClat$9dae12075f6826f63509e5ae8ac264726cdfa6f3ea9a9af57eaf6b9cf384dfe3edce6793e352adcca72a5912197ed89f784ba571ca76f33dad727f844e218358	mlstudent2003@gmail.com	support	\N
22	Anastasia	Anastasia	scrypt:32768:8:1$41jtLWZxRtMQbPTG$6b094ca4c413fc30afbf4f5ceeed5f4b6341a1601ab89a894949f67926040885450573837c8dcced44a02080d846e716ddc737047c62bae6b5b1f4a549b58338	m2105497@edu.misis.ru	admin	+79167574938
\.


--
-- TOC entry 4802 (class 0 OID 0)
-- Dependencies: 215
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 23, true);


--
-- TOC entry 4646 (class 2606 OID 16550)
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- TOC entry 4644 (class 2606 OID 16500)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 4647 (class 2606 OID 16559)
-- Name: user_roles fk_user_roles_role_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT fk_user_roles_role_id FOREIGN KEY (role_id) REFERENCES public.roles(id);


--
-- TOC entry 4648 (class 2606 OID 16554)
-- Name: user_roles fk_user_roles_user_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT fk_user_roles_user_id FOREIGN KEY (user_id) REFERENCES public.users(id);


-- Completed on 2024-07-16 14:47:49

--
-- PostgreSQL database dump complete
--

