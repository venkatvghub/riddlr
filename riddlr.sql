--
-- PostgreSQL database dump
--

-- Dumped from database version 13.1 (Debian 13.1-1.pgdg100+1)
-- Dumped by pg_dump version 13.1

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
-- Name: events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.events (
    id text NOT NULL,
    data text NOT NULL,
    current boolean DEFAULT false,
    "timestamp" date
);


ALTER TABLE public.events OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id text NOT NULL,
    password text NOT NULL,
    event text NOT NULL,
    level integer DEFAULT '-1'::integer NOT NULL,
    email text NOT NULL,
    phone text NOT NULL,
    ban boolean DEFAULT false,
    "timestamp" date
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Data for Name: events; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.events (id, data, current, "timestamp") FROM stdin;
foo	{"finish": "", "name": "The Foo Online Treasure Hunt", "faq": "https://example.com/example-oth/faq", "levels": [{"index": 1, "title": "The Dark Knight", "media": {"url": "http://vignette1.wikia.nocookie.net/batmananimateduniverse/images/2/20/Batman_tnba_pic.jpg/revision/latest?cb=20120209204824", "type": "img"}, "source": "Because we have to chase him. Because he's the hero Gotham deserves, but not the one it needs right now, so we'll hunt him. Because he can take it, because he's not a hero. He's a silent guardian, a watchful protector, a Dark Knight.", "text": "Who am I?", "answer": {"case": true, "hints": [], "choices": ["BATMAN"]}, "path": "dc/101"}, {"index": 2, "title": "Don't change in phone booths.", "media": {"url": "https://www.youtube.com/embed/oCOet3CPaa4", "type": "iframe"}, "source": "Kryptonite.", "text": "X is a fictional superhero appearing in American comic books published by DC Comics.", "answer": {"case": false, "hints": [{"text": "I'm not him, but we've never been in the same room.", "hint": "clark kent"}], "choices": ["superman"]}, "path": "lex"}, {"index": 3, "title": "Sintel", "media": {"url": "https://www.w3schools.com/html/mov_bbb.mp4", "type": "video"}, "source": "Open.", "text": "The what bunny?", "answer": {"case": false, "hints": [], "choices": ["big buck bunny", "the big buck bunny"]}, "path": "source"}, {"index": 4, "title": "The White.", "media": null, "source": "Beards.", "text": "All we have to decide is what to do with the time that is given to us.", "answer": {"case": false, "hints": [], "choices": ["gandalf"]}, "path": "wizard"}], "discuss": "https://example.com/example-oth/forums", "start": 1400000000, "host": "example-company", "intro": "A treasure hunt is one of many different types of games with one or more players who try to find hidden objects or places by following a series of clues. Treasure hunt games may be an indoor or outdoor activity. Outdoors they can be played in a garden or the treasure could be located anywhere around the world.", "social": "https://example.com/example-company", "id": "foo"}	f	2021-03-10
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, password, event, level, email, phone, ban, "timestamp") FROM stdin;
aaaa	$argon2id$v=19$m=102400,t=2,p=8$7ikFbz8wO9q3pNH08J9r8w$pv2lIiEHrJZuNY/iSV1IAQ	foo	2	aaa@bbb.com	9900121314	f	2021-03-11
\.


--
-- Name: events events_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_id_key UNIQUE (id);


--
-- Name: users users_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_id_key UNIQUE (id);


--
-- Name: index_event; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX index_event ON public.users USING btree (id);


--
-- Name: index_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX index_user ON public.users USING btree (id);


--
-- PostgreSQL database dump complete
--

