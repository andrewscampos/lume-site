#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import html
import json
import math
import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DATA = DATA_DIR / "programmatic-seo"
STATIC_SITEMAP = ROOT / "sitemap-static.xml"
PROGRAMMATIC_SITEMAP_1 = ROOT / "sitemap-programmatic-1.xml"
PROGRAMMATIC_SITEMAP_2 = ROOT / "sitemap-programmatic-2.xml"
SITEMAP_INDEX = ROOT / "sitemap.xml"
ROBOTS = ROOT / "robots.txt"
BASE_URL = "https://lumicode.com.br"
LOGO_URL = f"{BASE_URL}/img/logo-escrito.svg"
TODAY = date.today().isoformat()
SITEMAP_CHUNK_SIZE = 50000

STATE_REGIONS = {
    "AC": "Norte",
    "AL": "Nordeste",
    "AP": "Norte",
    "AM": "Norte",
    "BA": "Nordeste",
    "CE": "Nordeste",
    "DF": "Centro-Oeste",
    "ES": "Sudeste",
    "GO": "Centro-Oeste",
    "MA": "Nordeste",
    "MT": "Centro-Oeste",
    "MS": "Centro-Oeste",
    "MG": "Sudeste",
    "PA": "Norte",
    "PB": "Nordeste",
    "PR": "Sul",
    "PE": "Nordeste",
    "PI": "Nordeste",
    "RJ": "Sudeste",
    "RN": "Nordeste",
    "RS": "Sul",
    "RO": "Norte",
    "RR": "Norte",
    "SC": "Sul",
    "SP": "Sudeste",
    "SE": "Nordeste",
    "TO": "Norte",
}

CAPITALS = {
    "AC": "Rio Branco",
    "AL": "Maceió",
    "AP": "Macapá",
    "AM": "Manaus",
    "BA": "Salvador",
    "CE": "Fortaleza",
    "DF": "Brasília",
    "ES": "Vitória",
    "GO": "Goiânia",
    "MA": "São Luís",
    "MT": "Cuiabá",
    "MS": "Campo Grande",
    "MG": "Belo Horizonte",
    "PA": "Belém",
    "PB": "João Pessoa",
    "PR": "Curitiba",
    "PE": "Recife",
    "PI": "Teresina",
    "RJ": "Rio de Janeiro",
    "RN": "Natal",
    "RS": "Porto Alegre",
    "RO": "Porto Velho",
    "RR": "Boa Vista",
    "SC": "Florianópolis",
    "SP": "São Paulo",
    "SE": "Aracaju",
    "TO": "Palmas",
}

STATIC_URLS = [
    "/",
    "/index.html",
    "/blog.html",
    "/_blog.html",
    "/tipos-sites.html",
    "/adicionais.html",
    "/prazos.html",
    "/manutencao.html",
    "/politicas.html",
    "/privacy-policy.html",
    "/criacao-de-sites-profissionais.html",
    "/desenvolvimento-de-sistemas-em-sao-paulo.html",
    "/software-sob-medida.html",
    "/ecommerce-sob-medida.html",
    "/agencia-seo-sao-paulo.html",
    "/seo-programmatico.html",
    "/post/ia-transformacao-vendas-b2b-2026.html",
    "/post/como-escolher-agencia-tecnologia-2026.html",
    "/post/como-escolher-melhor-agencia-tecnologia.html",
    "/post/automacao-desafios-oportunidades-2026.html",
    "/post/revolucao-automacao-2026.html",
    "/post/transformacao-digital-futuro-empresas-2026.html",
]


@dataclass(frozen=True)
class State:
    id: int
    name: str
    abbr: str
    region: str


@dataclass(frozen=True)
class City:
    id: int
    name: str
    slug: str
    path_slug: str
    state_id: int
    state_name: str
    uf: str
    region: str
    population: int
    population_fmt: str
    is_capital: bool


@dataclass(frozen=True)
class Service:
    slug: str
    label: str
    short_focus: str
    service_type: str
    perspective: str
    benefits: tuple[str, ...]
    faqs: tuple[tuple[str, str], ...]


SERVICES = [
    Service(
        slug="desenvolvimento-de-sites",
        label="Desenvolvimento de Sites",
        short_focus="sites institucionais, landing pages e presença digital orientada a conversão",
        service_type="WebSite Development",
        perspective="atrai leads qualificados e fortalece a autoridade da marca",
        benefits=("visibilidade local", "conversão", "velocidade"),
        faqs=(
            ("Quanto tempo leva para publicar um site em {city}?", "O prazo depende do escopo, mas usamos um processo enxuto para lançar rapidamente, validar conteúdo e evoluir com testes."),
            ("Um site em {city} precisa de SEO técnico?", "Sim. Sem SEO técnico, o projeto perde desempenho em indexação, velocidade e usabilidade — pilares essenciais para ranquear."),
            ("Vocês adaptam o site para empresas de {city}?", "Sim. Ajustamos linguagem, prova social e chamadas para ação com contexto regional e foco no mercado local."),
            ("O site pode crescer junto com a empresa em {city}?", "Pode. A arquitetura é pensada para novas páginas, integrações e campanhas sem recomeçar do zero."),
        ),
    ),
    Service(
        slug="criacao-de-sites",
        label="Criação de Sites",
        short_focus="sites responsivos, branding digital e páginas de alta conversão",
        service_type="WebSite Creation",
        perspective="transforma a primeira impressão em oportunidades de negócio",
        benefits=("design responsivo", "arquitetura de conteúdo", "captação de demanda"),
        faqs=(
            ("Criação de sites em {city} inclui conteúdo?", "Inclui estrutura estratégica, páginas essenciais e orientação para textos que ajudam SEO e conversão."),
            ("O site fica pronto para Google e redes sociais?", "Sim. Trabalhamos meta tags, Open Graph, sitemap e fundamentos para compartilhamento e indexação."),
            ("A criação de site em {city} pode ser segmentada por serviço?", "Pode, e essa segmentação ajuda a capturar buscas específicas por bairro, cidade e intenção de compra."),
            ("Vocês entregam site com foco em conversão?", "Sim. Cada bloco é pensado para reduzir fricção e conduzir o usuário até o contato ou orçamento."),
        ),
    ),
    Service(
        slug="desenvolvimento-de-sistemas",
        label="Desenvolvimento de Sistemas",
        short_focus="ERP, CRM, portais internos e automações sob medida",
        service_type="Custom Software Development",
        perspective="organiza operações e reduz retrabalho com software empresarial",
        benefits=("automação", "integração", "escala"),
        faqs=(
            ("Quando vale criar um sistema em vez de adaptar um pronto?", "Quando o processo é estratégico, a adaptação custa caro ou a operação exige regras específicas e integrações próprias."),
            ("Sistemas para empresas de {city} podem integrar ERP e CRM?", "Sim. Integramos ERPs, CRMs, gateways, planilhas, APIs e legados para centralizar dados."),
            ("O sistema pode atender operações em várias filiais?", "Pode. Modelamos permissões, fluxos e relatórios multiunidade desde o início."),
            ("Vocês criam dashboards para empresas de {city}?", "Sim. Painéis executivos ajudam a acompanhar vendas, produtividade e indicadores em tempo real."),
        ),
    ),
    Service(
        slug="fabrica-de-software",
        label="Fábrica de Software",
        short_focus="times dedicados, squads e entrega contínua de produto",
        service_type="Software Factory",
        perspective="acelera roadmap com previsibilidade e governança",
        benefits=("time dedicado", "governança", "ritmo de entrega"),
        faqs=(
            ("Como funciona a fábrica de software em {city}?", "Estruturamos squads com gestão de backlog, rituais ágeis e documentação para evoluir o produto continuamente."),
            ("A fábrica de software atende projetos longos?", "Sim. É ideal para produtos com roadmap extenso, manutenção constante e novas versões recorrentes."),
            ("É possível começar pequeno e escalar depois?", "Sim. Começamos com o núcleo essencial e ampliamos conforme a demanda de negócio cresce."),
            ("Há acompanhamento de qualidade?", "Sim. Adotamos testes, revisão de código e critérios de aceite para manter consistência e estabilidade."),
        ),
    ),
    Service(
        slug="desenvolvimento-mobile",
        label="Desenvolvimento Mobile",
        short_focus="apps Android e iOS conectados a APIs e dados em tempo real",
        service_type="Mobile App Development",
        perspective="leva a experiência da marca para a palma da mão do cliente",
        benefits=("experiência móvel", "notificações", "fidelização"),
        faqs=(
            ("Aplicativos para empresas de {city} precisam de APIs próprias?", "Na maioria dos casos, sim. APIs bem definidas garantem performance, segurança e evolução do app."),
            ("Vocês desenvolvem apps Android e iOS?", "Sim. Escolhemos a abordagem nativa ou híbrida conforme prazo, custo e necessidade de performance."),
            ("Um app ajuda negócios locais em {city}?", "Ajuda quando existe recorrência, relacionamento ou operação com agendamento, pedido ou acompanhamento."),
            ("O app pode ter login e área do cliente?", "Pode, e isso é comum em produtos com histórico, status de pedidos, notificações e suporte."),
        ),
    ),
    Service(
        slug="desenvolvimento-java",
        label="Desenvolvimento Java",
        short_focus="backends corporativos, microsserviços e integrações críticas",
        service_type="Java Development",
        perspective="entrega robustez para sistemas de alta confiabilidade",
        benefits=("robustez", "segurança", "manutenibilidade"),
        faqs=(
            ("Java é indicado para empresas de {city}?", "Sim. É uma excelente escolha para plataformas críticas, integrações e operações com crescimento previsível."),
            ("Vocês usam Spring Boot em projetos Java?", "Sim. Spring Boot é uma base sólida para APIs, serviços e aplicações corporativas modernas."),
            ("Projetos Java suportam grande volume de dados?", "Suportam quando são desenhados com arquitetura, cache, filas e persistência bem estruturada."),
            ("É possível modernizar sistemas legados em Java?", "Sim. Fazemos refatoração incremental, novas APIs e evolução gradual sem interromper a operação."),
        ),
    ),
    Service(
        slug="desenvolvimento-vuejs",
        label="Desenvolvimento Vue.js",
        short_focus="interfaces rápidas, SPAs e painéis com ótima experiência do usuário",
        service_type="Vue.js Development",
        perspective="entrega frontends leves e fáceis de manter",
        benefits=("velocidade de interface", "componentização", "UX clara"),
        faqs=(
            ("Vue.js é bom para projetos em {city}?", "Sim. É ótimo para aplicações que precisam de agilidade visual, baixo atrito e boa manutenção."),
            ("Vocês desenvolvem dashboards com Vue.js?", "Sim. O framework é excelente para painéis administrativos, CRMs e backoffices."),
            ("Vue.js funciona com APIs próprias?", "Funciona muito bem, porque facilita separar interface e regras de negócio com clareza."),
            ("O frontend em Vue.js pode ser otimizado para SEO?", "Pode. Estruturamos HTML semântico, metadados e estratégias de renderização adequadas."),
        ),
    ),
    Service(
        slug="desenvolvimento-angular",
        label="Desenvolvimento Angular",
        short_focus="sistemas corporativos com estrutura, escalabilidade e componentes reutilizáveis",
        service_type="Angular Development",
        perspective="dá base sólida para aplicações complexas e times maiores",
        benefits=("arquitetura organizada", "escalabilidade", "padronização"),
        faqs=(
            ("Angular é indicado para empresas de {city}?", "Sim, principalmente quando o sistema tem muitos módulos, formulários e regras de negócio interdependentes."),
            ("Angular ajuda em projetos grandes?", "Ajuda porque favorece organização, padronização e evolução com equipes maiores."),
            ("Vocês integram Angular com backends Java?", "Sim. É uma combinação muito comum em sistemas corporativos e portais internos."),
            ("É possível criar áreas administrativas em Angular?", "Sim. É uma das melhores opções para backoffices, CRMs e dashboards ricos."),
        ),
    ),
    Service(
        slug="inteligencia-artificial",
        label="Inteligência Artificial",
        short_focus="assistentes, automações, recomendação e análise inteligente",
        service_type="Artificial Intelligence",
        perspective="aumenta produtividade com decisões mais rápidas e menos trabalho manual",
        benefits=("eficiência", "automação cognitiva", "análise preditiva"),
        faqs=(
            ("Como IA pode ajudar empresas de {city}?", "Ela automatiza atendimento, classificação de dados, geração de respostas e apoio à tomada de decisão."),
            ("É possível usar IA com dados internos?", "Sim, desde que haja governança, segurança e base de dados estruturada para consulta e aprendizado."),
            ("A IA substitui equipes?", "Não necessariamente. Ela reduz tarefas repetitivas e libera pessoas para atividades de maior valor."),
            ("Vocês criam soluções de IA sob medida?", "Sim. Avaliamos o problema, a qualidade dos dados e o retorno esperado antes de propor a arquitetura."),
        ),
    ),
    Service(
        slug="chatbot-whatsapp",
        label="Chatbot WhatsApp",
        short_focus="automação de atendimento, qualificação de leads e integração com CRM",
        service_type="WhatsApp Chatbot",
        perspective="responde rápido, capta oportunidades e organiza o funil",
        benefits=("resposta imediata", "qualificação", "atendimento 24/7"),
        faqs=(
            ("Chatbot WhatsApp funciona para empresas de {city}?", "Sim. Ele acelera o atendimento, reduz filas e melhora a experiência do cliente local."),
            ("O bot pode integrar com CRM e ERP?", "Pode. Essa integração ajuda a registrar leads, tickets, pedidos e históricos em um só lugar."),
            ("É possível usar chatbot para vendas?", "Sim. Ele qualifica contato, direciona ofertas e encaminha leads prontos para o comercial."),
            ("Vocês monitoram a qualidade das respostas?", "Sim. Acompanhamos métricas e refinamos fluxos para reduzir falhas e aumentar conversão."),
        ),
    ),
    Service(
        slug="automacao-empresarial",
        label="Automação Empresarial",
        short_focus="workflows, integrações e eliminação de tarefas repetitivas",
        service_type="Business Automation",
        perspective="reduz custo operacional e melhora a velocidade da empresa",
        benefits=("menos retrabalho", "integração de sistemas", "produtividade"),
        faqs=(
            ("Quais processos podem ser automatizados em {city}?", "Vendas, financeiro, suporte, cadastro, atualização de status, integrações e relatórios recorrentes."),
            ("A automação empresarial precisa de sistemas novos?", "Nem sempre. Muitas vezes conectamos sistemas existentes para eliminar tarefas manuais."),
            ("Automação reduz erros operacionais?", "Sim. Regras automáticas diminuem digitação manual, duplicidade e falhas de sincronização."),
            ("É possível automatizar com segurança?", "Sim. Usamos logs, permissões, monitoramento e validações para manter controle e rastreabilidade."),
        ),
    ),
]


@dataclass(frozen=True)
class CityServicePage:
    slug: str
    url: str
    title: str
    description: str
    content: str



def fetch_json(url: str):
    request = Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json", "Accept-Encoding": "gzip"})
    with urlopen(request, timeout=60) as response:
        raw = response.read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = gzip.decompress(raw).decode("utf-8")
    if text and text[0] == "\ufeff":
        text = text[1:]
    return json.loads(text)


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower().replace("`", "").replace("'", "")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value


def number_fmt(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def page_slug(service: Service, city: City) -> str:
    return f"{service.slug}-{city.path_slug}"


def market_profile(city: City) -> tuple[str, str]:
    pop = city.population
    if pop >= 1_000_000:
        scale = "um mercado metropolitano de grande porte, com muita concorrência e forte disputa por atenção"
        opportunity = "isso exige posicionamento claro, tecnologia rápida e uma jornada digital capaz de capturar demanda em alta escala"
    elif pop >= 250_000:
        scale = "um polo regional robusto, com demanda qualificada e empresas que competem por autoridade online"
        opportunity = "a estratégia ideal combina conteúdo local, experiência de usuário e páginas com foco em conversão"
    elif pop >= 80_000:
        scale = "uma cidade em expansão com espaço para diferenciação digital e aquisição previsível de clientes"
        opportunity = "o ganho vem de presença consistente, prova social e landing pages orientadas a serviços específicos"
    else:
        scale = "um mercado mais enxuto, onde proximidade, reputação e agilidade comercial fazem diferença"
        opportunity = "a mensagem precisa ser direta, com SEO local e chamadas para ação que reforcem confiança e contato rápido"
    return scale, opportunity


def service_angle(service: Service, city: City) -> str:
    capital_note = f"{city.name} é capital estadual" if city.is_capital else f"{city.name} atua como referência regional no estado de {city.state_name}"
    if service.slug in {"desenvolvimento-de-sites", "criacao-de-sites"}:
        return f"{capital_note}, por isso um site bem estruturado ajuda a transformar buscas locais em oportunidades reais de orçamento e contato."
    if service.slug == "desenvolvimento-de-sistemas":
        return f"{capital_note}, então sistemas personalizados ajudam a padronizar processos e integrar equipes sem depender de planilhas dispersas."
    if service.slug == "fabrica-de-software":
        return f"{capital_note}, o que favorece operações com roadmap contínuo, squads dedicados e evolução constante do produto digital."
    if service.slug == "desenvolvimento-mobile":
        return f"{capital_note}, e aplicativos bem desenhados ampliam relacionamento, retenção e recorrência de uso do seu serviço."
    if service.slug in {"desenvolvimento-java", "desenvolvimento-vuejs", "desenvolvimento-angular"}:
        return f"{capital_note}, o que pede engenharia de software organizada para sustentar interfaces, APIs e integrações com escala."
    if service.slug == "inteligencia-artificial":
        return f"{capital_note}, então IA pode acelerar atendimento, análise e automação em contextos com fluxo crescente de dados."
    if service.slug == "chatbot-whatsapp":
        return f"{capital_note}, por isso um chatbot de WhatsApp ajuda a responder rápido, qualificar leads e distribuir demandas com eficiência."
    return f"{capital_note}, o que torna a automação empresarial um caminho direto para reduzir retrabalho e liberar tempo da equipe."


def city_intro(city: City, service: Service) -> str:
    scale, opportunity = market_profile(city)
    opportunity = opportunity[0].upper() + opportunity[1:]
    return (
        f"Na prática, {city.name} ({city.uf}) reúne {scale}. "
        f"A população estimada de {city.population_fmt} habitantes coloca a cidade em um cenário de oportunidades para empresas que querem crescer com estratégia digital. "
        f"{opportunity}. {service_angle(service, city)}"
    )


def service_section_text(service: Service, city: City) -> str:
    scale, _ = market_profile(city)
    base = f"Em {city.name}, {service.short_focus.lower()} precisa conversar com {scale}."
    if service.slug == "desenvolvimento-de-sites":
        return base + " Um site bem planejado combina arquitetura da informação, SEO local, CTA visível e performance para converter tráfego em conversas comerciais."
    if service.slug == "criacao-de-sites":
        return base + " A criação do site precisa unir identidade visual, copy persuasiva e estrutura de páginas que facilite a descoberta pelo Google e pelo usuário."
    if service.slug == "desenvolvimento-de-sistemas":
        return base + " Os sistemas devem refletir processos da operação, com integrações, permissões e relatórios que reduzam fricção no dia a dia."
    if service.slug == "fabrica-de-software":
        return base + " A fábrica de software funciona melhor quando o backlog é priorizado por valor e a equipe entrega em ciclos curtos com qualidade constante."
    if service.slug == "desenvolvimento-mobile":
        return base + " Aplicativos móveis ajudam a criar recorrência e relacionamento, especialmente quando conectados a APIs estáveis e notificações relevantes."
    if service.slug == "desenvolvimento-java":
        return base + " Java entrega robustez para regras complexas, integrações críticas e sistemas corporativos com exigência de manutenção de longo prazo."
    if service.slug == "desenvolvimento-vuejs":
        return base + " Vue.js é excelente quando a interface precisa ser fluida, modular e fácil de manter ao longo do crescimento do produto."
    if service.slug == "desenvolvimento-angular":
        return base + " Angular é uma boa escolha quando a aplicação possui muitos módulos, formulários e equipes que exigem padronização forte."
    if service.slug == "inteligencia-artificial":
        return base + " IA pode atuar em automação de atendimento, sumarização, classificação de dados e apoio à decisão com governança."
    if service.slug == "chatbot-whatsapp":
        return base + " O chatbot precisa responder rápido, encaminhar conversas e transformar canais de atendimento em uma operação previsível."
    return base + " A automação empresarial deve conectar sistemas, eliminar digitação repetitiva e reduzir erros que custam tempo e dinheiro."


def benefit_bullets(service: Service, city: City) -> list[str]:
    bullets = []
    for benefit in service.benefits:
        if benefit == "visibilidade local":
            bullets.append(f"Aumenta a visibilidade local de empresas de {city.name} nos resultados do Google.")
        elif benefit == "conversão":
            bullets.append(f"Melhora a conversão de visitantes em leads qualificados em {city.name}.")
        elif benefit == "velocidade":
            bullets.append(f"Entrega páginas rápidas, úteis e prontas para SEO em {city.name}.")
        elif benefit == "design responsivo":
            bullets.append(f"Garante experiência responsiva em qualquer dispositivo usado pelo público de {city.name}.")
        elif benefit == "arquitetura de conteúdo":
            bullets.append(f"Organiza o conteúdo para pesquisas locais e intenção comercial em {city.name}.")
        elif benefit == "captação de demanda":
            bullets.append(f"Ajuda a captar demanda orgânica e campanhas pagas voltadas ao mercado de {city.name}.")
        elif benefit == "automação":
            bullets.append(f"Automatiza rotinas críticas de empresas de {city.name} sem perder controle operacional.")
        elif benefit == "integração":
            bullets.append(f"Integra sistemas que a operação de {city.name} já usa no dia a dia.")
        elif benefit == "escala":
            bullets.append(f"Prepara a solução para crescer junto com o negócio em {city.name}.")
        elif benefit == "time dedicado":
            bullets.append(f"Oferece uma estrutura de squad dedicada para demandas recorrentes em {city.name}.")
        elif benefit == "governança":
            bullets.append(f"Mantém governança clara para acompanhar entregas e qualidade em {city.name}.")
        elif benefit == "ritmo de entrega":
            bullets.append(f"Sustenta um ritmo de entrega constante para negócios de {city.name}.")
        elif benefit == "experiência móvel":
            bullets.append(f"Leva a experiência do cliente de {city.name} para um aplicativo útil no dia a dia.")
        elif benefit == "notificações":
            bullets.append(f"Ativa notificações estratégicas para reengajamento de clientes em {city.name}.")
        elif benefit == "fidelização":
            bullets.append(f"Ajuda a fidelizar usuários e aumentar recorrência em {city.name}.")
        elif benefit == "robustez":
            bullets.append(f"Aumenta a robustez técnica de sistemas críticos usados em {city.name}.")
        elif benefit == "segurança":
            bullets.append(f"Reforça segurança e controle de acesso em aplicações corporativas de {city.name}.")
        elif benefit == "manutenibilidade":
            bullets.append(f"Facilita manutenção e evolução contínua das soluções de {city.name}.")
        elif benefit == "velocidade de interface":
            bullets.append(f"Entrega interfaces rápidas e fluidas para equipes e clientes de {city.name}.")
        elif benefit == "componentização":
            bullets.append(f"Permite reaproveitar componentes e acelerar entregas em {city.name}.")
        elif benefit == "UX clara":
            bullets.append(f"Garante uma experiência clara para usuários e administradores em {city.name}.")
        elif benefit == "arquitetura organizada":
            bullets.append(f"Organiza grandes aplicações com clareza e previsibilidade em {city.name}.")
        elif benefit == "escalabilidade":
            bullets.append(f"Suporta crescimento de uso e novas funcionalidades em {city.name}.")
        elif benefit == "padronização":
            bullets.append(f"Padroniza a base técnica para equipes que operam em {city.name}.")
        elif benefit == "eficiência":
            bullets.append(f"Aumenta a eficiência operacional de empresas de {city.name}.")
        elif benefit == "automação cognitiva":
            bullets.append(f"Aplica automação cognitiva em fluxos importantes do mercado de {city.name}.")
        elif benefit == "análise preditiva":
            bullets.append(f"Permite análises preditivas para decisões mais rápidas em {city.name}.")
        elif benefit == "resposta imediata":
            bullets.append(f"Responde imediatamente às mensagens recebidas de clientes em {city.name}.")
        elif benefit == "qualificação":
            bullets.append(f"Qualifica leads antes do contato humano em {city.name}.")
        elif benefit == "atendimento 24/7":
            bullets.append(f"Mantém atendimento 24/7 para negócios de {city.name}.")
        elif benefit == "menos retrabalho":
            bullets.append(f"Reduz retrabalho e tarefas repetitivas em operações de {city.name}.")
        elif benefit == "integração de sistemas":
            bullets.append(f"Conecta sistemas e bases de dados usados por empresas de {city.name}.")
        elif benefit == "produtividade":
            bullets.append(f"Melhora a produtividade das equipes que atuam em {city.name}.")
        else:
            bullets.append(f"{benefit.title()} para empresas de {city.name}.")
    return bullets


def faq_items(service: Service, city: City) -> list[tuple[str, str]]:
    items = []
    for question, answer in service.faqs:
        q = question.format(city=city.name)
        a = answer.format(city=city.name)
        items.append((q, a))
    return items


def breadcrumb_jsonld(url: str, service: Service, city: City) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE_URL + "/"},
            {"@type": "ListItem", "position": 2, "name": service.label, "item": f"{BASE_URL}/{service.slug}"},
            {"@type": "ListItem", "position": 3, "name": city.name, "item": url},
        ],
    }


def build_schema(url: str, service: Service, city: City) -> str:
    faqs = faq_items(service, city)
    schema = [
        {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": "LumiCode",
            "url": BASE_URL,
            "logo": LOGO_URL,
            "image": LOGO_URL,
            "description": f"LumiCode oferece {service.label.lower()} em {city.name}, {city.uf}.",
            "address": {
                "@type": "PostalAddress",
                "addressLocality": city.state_name,
                "addressRegion": city.uf,
                "addressCountry": "BR",
            },
            "areaServed": {
                "@type": "City",
                "name": city.name,
            },
            "telephone": "+55-11-94957-7030",
            "email": "contato@lumicode.com.br",
            "priceRange": "$$",
        },
        {
            "@context": "https://schema.org",
            "@type": "Service",
            "name": f"{service.label} em {city.name}",
            "serviceType": service.service_type,
            "provider": {
                "@type": "Organization",
                "name": "LumiCode",
                "url": BASE_URL,
                "logo": LOGO_URL,
            },
            "areaServed": {
                "@type": "City",
                "name": city.name,
            },
            "description": f"{service.label} para empresas de {city.name} ({city.uf}).",
        },
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": question,
                    "acceptedAnswer": {"@type": "Answer", "text": answer},
                }
                for question, answer in faqs
            ],
        },
        breadcrumb_jsonld(url, service, city),
    ]
    return "<script type=\"application/ld+json\">" + json.dumps(schema, ensure_ascii=False, separators=(",", ":")) + "</script>"


def render_page(city: City, service: Service) -> CityServicePage:
    slug = page_slug(service, city)
    url = f"{BASE_URL}/{slug}"
    title = f"{service.label} em {city.name} | LumiCode"
    description = (
        f"{service.label} em {city.name} ({city.uf}). "
        f"{service.perspective.capitalize()} para empresas da região {city.region} com uma base populacional de {city.population_fmt} habitantes."
    )
    intro = city_intro(city, service)
    market_scale, market_opportunity = market_profile(city)
    market_opportunity_sentence = market_opportunity[0].upper() + market_opportunity[1:]
    bullets = benefit_bullets(service, city)
    faqs = faq_items(service, city)
    city_h2 = f"Panorama de {city.name} ({city.uf}) e do mercado local"
    content_html = f"""
    <main class="page">
      <section class="hero">
        <div class="crumbs">Home &gt; {html.escape(service.label)} &gt; {html.escape(city.name)}</div>
        <p class="eyebrow">SEO Programático • {html.escape(service.label)}</p>
        <h1>{html.escape(service.label)} em {html.escape(city.name)}</h1>
        <p class="lead">{html.escape(intro)}</p>
      </section>

      <section class="content-card">
        <h2>{html.escape(city_h2)}</h2>
        <p>{html.escape(f"{city.name} fica no estado de {city.state_name} ({city.uf}), na região {city.region}. Com {city.population_fmt} habitantes, a cidade representa {market_scale}.")}</p>
        <p>{html.escape(market_opportunity_sentence)}.</p>
        <p>{html.escape(f"A seguir, a abordagem de {service.label.lower()} é adaptada ao contexto de {city.name}, com foco em autoridade, clareza comercial e crescimento sustentável.")}</p>
      </section>

      <section class="content-card">
        <h2>Como {html.escape(service.label.lower())} ajuda empresas de {html.escape(city.name)}</h2>
        <p>{html.escape(service_section_text(service, city))}</p>
        <ul>
          {''.join(f'<li>{html.escape(item)}</li>' for item in bullets)}
        </ul>
      </section>

      <section class="content-card">
        <h2>FAQ sobre {html.escape(service.label.lower())} em {html.escape(city.name)}</h2>
        {''.join(f'<details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>' for q, a in faqs)}
      </section>
    </main>
    """
    schema = build_schema(url, service, city)
    html_doc = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(description)}">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <link rel="canonical" href="{html.escape(url)}">
  <link rel="icon" href="/img/favicon.ico" type="image/x-icon">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="pt_BR">
  <meta property="og:url" content="{html.escape(url)}">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(description)}">
  <meta property="og:image" content="{LOGO_URL}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html.escape(title)}">
  <meta name="twitter:description" content="{html.escape(description)}">
  <meta name="twitter:image" content="{LOGO_URL}">
  <style>
    :root {{ --bg:#0d1117; --panel:#111827; --line:#243044; --text:#e5e7eb; --muted:#aeb8c5; --accent:#60f47b; --accent2:#9ef0ad; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif; background:linear-gradient(180deg,#0b1220,#111827 55%,#0b1220); color:var(--text); line-height:1.65; }}
    a {{ color:var(--accent2); text-decoration:none; }}
    .topbar {{ padding:18px 24px; border-bottom:1px solid rgba(255,255,255,.06); backdrop-filter: blur(10px); position:sticky; top:0; background:rgba(10,15,25,.78); z-index:2; }}
    .topbar .brand {{ display:flex; align-items:center; gap:14px; max-width:1120px; margin:0 auto; }}
    .topbar img {{ height:30px; }}
    .topbar nav {{ margin-left:auto; display:flex; gap:18px; flex-wrap:wrap; font-size:14px; color:var(--muted); }}
    .page {{ max-width:1120px; margin:0 auto; padding:48px 24px 72px; }}
    .hero {{ background:linear-gradient(135deg, rgba(96,244,123,.14), rgba(255,255,255,.03)); border:1px solid rgba(96,244,123,.25); border-radius:24px; padding:36px; box-shadow:0 16px 60px rgba(0,0,0,.25); }}
    .crumbs, .eyebrow {{ color:var(--accent); text-transform:uppercase; letter-spacing:.08em; font-size:12px; font-weight:700; }}
    h1 {{ margin:10px 0 12px; font-size:clamp(2rem, 5vw, 3.7rem); line-height:1.05; }}
    h2 {{ font-size:clamp(1.4rem, 3vw, 2rem); margin:0 0 14px; }}
    .lead {{ font-size:1.08rem; color:var(--text); max-width:900px; }}
    .content-card {{ margin-top:24px; background:rgba(17,24,39,.88); border:1px solid var(--line); border-radius:22px; padding:28px; }}
    .content-card p {{ color:var(--text); }}
    ul {{ padding-left:20px; }}
    li {{ margin:10px 0; color:var(--text); }}
    details {{ border-top:1px solid var(--line); padding:14px 0; }}
    details:last-child {{ border-bottom:1px solid var(--line); }}
    summary {{ cursor:pointer; font-weight:700; color:var(--accent2); }}
    footer {{ max-width:1120px; margin:0 auto; padding:0 24px 48px; color:var(--muted); font-size:14px; }}
    @media (max-width: 700px) {{ .hero, .content-card {{ padding:22px; }} .topbar nav {{ display:none; }} }}
  </style>
  {schema}
</head>
<body>
  <header class="topbar">
    <div class="brand">
      <a href="/index.html"><img src="{LOGO_URL}" alt="LumiCode"></a>
      <nav>
        <a href="/index.html">Home</a>
        <a href="/seo-programmatico.html">SEO Programático</a>
        <a href="/blog.html">Blog</a>
        <a href="/agencia-seo-sao-paulo.html">SEO</a>
      </nav>
    </div>
  </header>
  {content_html}
  <footer>
    <p>LumiCode • conteúdo programático de {html.escape(service.label.lower())} para {html.escape(city.name)} ({html.escape(city.uf)}).</p>
    <p><a href="/sitemap.xml">Sitemap</a> • <a href="/robots.txt">Robots.txt</a></p>
  </footer>
</body>
</html>
"""
    return CityServicePage(slug=slug, url=url, title=title, description=description, content=html_doc)


def load_states() -> dict[int, State]:
    raw = fetch_json("https://raw.githubusercontent.com/magnobiet/states-cities-brazil/main/JSON/states.json")
    return {
        int(item["id"]): State(
            id=int(item["id"]),
            name=item["name"],
            abbr=item["abbr"],
            region=STATE_REGIONS[item["abbr"]],
        )
        for item in raw
    }


def load_cities(states: dict[int, State]) -> list[dict]:
    raw = fetch_json("https://raw.githubusercontent.com/magnobiet/states-cities-brazil/main/JSON/cities.json")
    return [
        {
            "id": int(item["id"]),
            "name": item["name"],
            "slug": slugify(item["name"]),
            "state_id": int(item["state_id"]),
            "state_name": states[int(item["state_id"])].name,
            "uf": states[int(item["state_id"])].abbr,
            "region": states[int(item["state_id"])].region,
            "is_capital": item["name"] == CAPITALS[states[int(item["state_id"])].abbr],
        }
        for item in raw
    ]


def load_population_2025() -> dict[int, int]:
    # Table 6579 = population estimates; period 2025; D3C 9324 = population residente estimada.
    raw = fetch_json("https://apisidra.ibge.gov.br/values/t/6579/n6/all/p/2025/h/n")
    population = {}
    for row in raw:
        if row.get("D3C") != "9324":
            continue
        try:
            population[int(row["D1C"])] = int(str(row["V"]).replace(".", ""))
        except Exception:
            continue
    return population


def build_city_records() -> list[City]:
    states = load_states()
    cities = load_cities(states)
    population = load_population_2025()
    interim = []
    missing = []
    for item in cities:
        pop = population.get(item["id"])
        if pop is None:
            missing.append(item["name"])
            continue
        interim.append({**item, "population": pop, "population_fmt": number_fmt(pop)})
    if missing:
        print(f"[warn] Cities without population data: {len(missing)}")
        print("[warn] Sample missing:", ", ".join(missing[:10]))

    from collections import Counter

    slug_counts = Counter(item["slug"] for item in interim)
    records = []
    for item in interim:
        path_slug = item["slug"] if slug_counts[item["slug"]] == 1 else f"{item['slug']}-{item['uf'].lower()}"
        records.append(
            City(
                id=item["id"],
                name=item["name"],
                slug=item["slug"],
                path_slug=path_slug,
                state_id=item["state_id"],
                state_name=item["state_name"],
                uf=item["uf"],
                region=item["region"],
                population=item["population"],
                population_fmt=item["population_fmt"],
                is_capital=item["is_capital"],
            )
        )
    records.sort(key=lambda c: (c.state_name, c.name))
    return records


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def build_static_sitemap_urls() -> list[str]:
    urls = []
    for item in STATIC_URLS:
        if item == "/":
            loc = BASE_URL + "/"
        else:
            loc = BASE_URL + item
        urls.append(loc)
    return urls


def make_urlset(urls: Iterable[str]) -> str:
    parts = ["<?xml version=\"1.0\" encoding=\"UTF-8\"?>", '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in urls:
        parts.append("  <url>")
        parts.append(f"    <loc>{html.escape(url)}</loc>")
        parts.append(f"    <lastmod>{TODAY}</lastmod>")
        parts.append("    <changefreq>weekly</changefreq>")
        parts.append("    <priority>0.8</priority>")
        parts.append("  </url>")
    parts.append("</urlset>")
    return "\n".join(parts) + "\n"


def make_sitemap_index(entries: list[tuple[str, str]]) -> str:
    parts = ["<?xml version=\"1.0\" encoding=\"UTF-8\"?>", '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, modified in entries:
        parts.append("  <sitemap>")
        parts.append(f"    <loc>{html.escape(loc)}</loc>")
        parts.append(f"    <lastmod>{modified}</lastmod>")
        parts.append("  </sitemap>")
    parts.append("</sitemapindex>")
    return "\n".join(parts) + "\n"


def build_programmatic_pages(cities: list[City], services: list[Service]) -> list[CityServicePage]:
    pages = []
    for city in cities:
        for service in services:
            pages.append(render_page(city, service))
    return pages


def write_programmatic_pages(pages: list[CityServicePage]) -> None:
    for idx, page in enumerate(pages, start=1):
        output = ROOT / f"{page.slug}.html"
        write_text(output, page.content)
        if idx % 1000 == 0:
            print(f"[pages] wrote {idx}/{len(pages)}")


def cleanup_stale_programmatic_pages(pages: list[CityServicePage]) -> None:
    desired = {ROOT / f"{page.slug}.html" for page in pages}
    preserved_root_names = {
        Path(item.lstrip("/")).name
        for item in STATIC_URLS
        if item != "/" and "/" not in item.lstrip("/")
    }
    for existing in ROOT.glob("*.html"):
        if existing in desired:
            continue
        if existing.name in preserved_root_names:
            continue
        if any(existing.stem.startswith(service.slug + "-") for service in SERVICES):
            existing.unlink()


def write_data_files(cities: list[City]) -> None:
    payload = [
        {
            "id": c.id,
            "name": c.name,
            "slug": c.slug,
            "path_slug": c.path_slug,
            "state_id": c.state_id,
            "state_name": c.state_name,
            "uf": c.uf,
            "region": c.region,
            "population": c.population,
            "population_fmt": c.population_fmt,
            "is_capital": c.is_capital,
        }
        for c in cities
    ]
    write_json(OUTPUT_DATA.with_suffix(".json"), payload)
    write_json(DATA_DIR / "programmatic-seo-meta.json", {
        "generated_at": TODAY,
        "cities": len(cities),
        "services": len(SERVICES),
        "pages": len(cities) * len(SERVICES),
        "source_population_period": 2025,
        "source_population_table": 6579,
        "source_population_variable": 9324,
    })


def write_sitemaps(pages: list[CityServicePage]) -> None:
    static_urls = build_static_sitemap_urls()
    write_text(STATIC_SITEMAP, make_urlset(static_urls))

    page_urls = [page.url for page in pages]
    chunks = [page_urls[i : i + SITEMAP_CHUNK_SIZE] for i in range(0, len(page_urls), SITEMAP_CHUNK_SIZE)]
    chunk_files = []
    for idx, chunk in enumerate(chunks, start=1):
        if idx == 1:
            path = PROGRAMMATIC_SITEMAP_1
        elif idx == 2:
            path = PROGRAMMATIC_SITEMAP_2
        else:
            path = ROOT / f"sitemap-programmatic-{idx}.xml"
        write_text(path, make_urlset(chunk))
        chunk_files.append(path)

    entries = [
        (f"{BASE_URL}/sitemap-static.xml", TODAY),
    ] + [(f"{BASE_URL}/{path.name}", TODAY) for path in chunk_files]
    write_text(SITEMAP_INDEX, make_sitemap_index(entries))

    write_text(
        ROBOTS,
        "\n".join(
            [
                "User-agent: *",
                "Allow: /",
                "",
                f"Sitemap: {BASE_URL}/sitemap.xml",
                "",
                "Disallow: /admin/",
                "Disallow: /private/",
                "Disallow: /temp/",
                "",
                "Crawl-delay: 1",
                "",
            ]
        ),
    )


def write_hub_page(cities: list[City]) -> None:
    top_cities = sorted(cities, key=lambda c: c.population, reverse=True)[:24]
    service_links = "\n".join(
        f'<li><a href="/{service.slug}-{top_cities[0].path_slug}.html">{html.escape(service.label)}</a> — {html.escape(service.short_focus)}</li>'
        for service in SERVICES
    )
    city_links = "\n".join(
        f'<li>{html.escape(city.name)} ({html.escape(city.uf)}) — {city.population_fmt} habitantes</li>'
        for city in top_cities
    )
    page = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SEO Programático para Serviços em Cidades Brasileiras | LumiCode</title>
  <meta name="description" content="Estratégia programática da LumiCode para gerar páginas locais por serviço e cidade no Brasil, com SEO, schema, sitemap e conteúdo único.">
  <link rel="canonical" href="{BASE_URL}/seo-programmatico">
  <style>
    body {{ font-family: system-ui, sans-serif; margin:0; background:#0b1220; color:#e5e7eb; }}
    main {{ max-width:1000px; margin:0 auto; padding:48px 24px; }}
    .card {{ background:#111827; border:1px solid #243044; border-radius:20px; padding:24px; margin:18px 0; }}
    a {{ color:#9ef0ad; }}
  </style>
</head>
<body>
  <main>
    <h1>SEO Programático da LumiCode</h1>
    <p>Base: {len(cities)} cidades brasileiras, {len(SERVICES)} serviços e uma estrutura pensada para escala, conteúdo único e indexação contínua.</p>
    <div class="card">
      <h2>Serviços</h2>
      <ul>{service_links}</ul>
    </div>
    <div class="card">
      <h2>Cidades com maior população no conjunto</h2>
      <ul>{city_links}</ul>
    </div>
    <div class="card">
      <h2>Diretrizes implementadas</h2>
      <ul>
        <li>Title, meta description, H1 e H2 únicos por página.</li>
        <li>Schema.org com LocalBusiness, Service, FAQPage e BreadcrumbList.</li>
        <li>Open Graph e Twitter Cards automáticos.</li>
        <li>Sitemap em índice com chunking para respeitar o limite de 50 mil URLs por arquivo.</li>
        <li>Robots.txt permitindo indexação e apontando para o sitemap.</li>
      </ul>
    </div>
  </main>
</body>
</html>
"""
    write_text(ROOT / "seo-programmatico.html", page)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate programmatic SEO pages for Brazilian cities.")
    parser.add_argument("--skip-pages", action="store_true", help="Only generate data and sitemap files.")
    parser.add_argument("--limit-cities", type=int, default=None, help="Limit cities for local testing.")
    args = parser.parse_args()

    print("[data] loading cities and population sources...")
    cities = build_city_records()
    if args.limit_cities is not None:
        cities = cities[: args.limit_cities]
        print(f"[data] limited to {len(cities)} cities")

    write_data_files(cities)
    write_hub_page(cities)

    pages = build_programmatic_pages(cities, SERVICES)
    print(f"[pages] generated {len(pages)} pages in memory")

    cleanup_stale_programmatic_pages(pages)
    if not args.skip_pages:
        write_programmatic_pages(pages)
    write_sitemaps(pages)

    print("[done]")
    print(f"cities={len(cities)} services={len(SERVICES)} pages={len(pages)}")
    print(f"sitemap index: {SITEMAP_INDEX}")
    print(f"robots: {ROBOTS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
