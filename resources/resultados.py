import copy
import json
import math
import os as osL
import sys
import uuid

import reportlab
from flask import Response, request, jsonify, make_response
from flask_babel import gettext
from flask_jwt_extended import jwt_required, get_jwt_identity
from html2image import Html2Image
from pyvis.network import Network
from sqlalchemy import and_

from reportlab.graphics.shapes import Drawing, Line
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, inch, portrait, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, ListFlowable, ListItem, PageBreak, \
    Flowable, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

from database import db
from database.models.alumno import Alumno, AlumnosClase
from database.models.clase import Clase
from database.models.colegio import Colegio
from database.models.picto import Picto
from database.models.preferencias import Preferencias
from database.models.pregunta import Pregunta
from database.models.profesor import Profesor
from database.models.test import Test, AlumnosTest, Respuesta, PreguntasTest
from database.models.user import User
from database.models.grupoEdad import GrupoEdad
from database.models.link import Link
from database.models.tipoPregunta import TipoPregunta
from database.models.tipoEstructura import TipoEstructura

from flask_restful import Resource

from resources.errors import SchemaValidationError, InternalServerError, PreguntaNotExistsError, NotResults
from resources.decorators import profesor, alumno, superuser
from resources.footerCanvas import FooterCanvas

from PIL import Image

MAX_POINTS = 5
MIN_POINTS = 1
MIDDLE_POINT = int(round((MAX_POINTS + MIN_POINTS) / 2))

# CONFIGURAR ESTILO TABLA
style1 = [
    ('LINEBELOW', (0, 0), (-1, -2), 0.25, colors.gray),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
    ('LINEABOVE', (0, 0), (-1, 0), 1, colors.gray)
]

style2 = [
    ('LINEBELOW', (0, 1), (-1, -1), 0.25, colors.gray),
    ('LINEBELOW', (0, 0), (-1, 0), 1, colors.gray),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
    ('LINEABOVE', (0, 0), (-1, 0), 1, colors.white),
    ('LINEBEFORE', (1, 1), (-1, 1), 0.25, colors.gray),
    ('LINEBEFORE', (1, -1), (-1, -1), 0.25, colors.gray)
]

style3 = [
    ('LINEBELOW', (0, 1), (-1, -2), 0.25, colors.gray),
    ('LINEBELOW', (0, 0), (-1, 0), 1, colors.gray),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
    ('LINEABOVE', (0, 0), (-1, 0), 1, colors.white)
]

style4 = [
    ('LINEBELOW', (0, 1), (-1, -2), 0.25, colors.gray),
    ('LINEBELOW', (0, 0), (-1, 0), 1, colors.gray),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
    ('LINEABOVE', (0, 0), (-1, 0), 1, colors.white),
    ('LINEBEFORE', (1, 1), (-1, -1), 0.25, colors.gray)
]

style5 = [
    ('LINEBELOW', (0, 0), (-1, -2), 0.25, colors.gray),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
]

style6 = [
    ('LINEABOVE', (0, 0), (1, 0), 0.25, colors.gray),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
    ('BACKGROUND', (0, 0), (0, 0), colors.HexColor("#d6c22b"))  # amarillo
]

style7 = [
    ('LINEABOVE', (0, 0), (1, 0), 0.25, colors.gray),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
    ('BACKGROUND', (0, 0), (0, 0), colors.HexColor("#0da863"))  # verde
]

style8 = [
    ('LINEABOVE', (0, 0), (1, 0), 0.25, colors.gray),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
    ('BACKGROUND', (0, 0), (0, 0), colors.HexColor("#e05ab8"))  # rosa
]

style9 = [
    ('LINEABOVE', (0, 0), (1, -1), 0.25, colors.gray),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
    ('BACKGROUND', (0, 0), (0, 0), colors.HexColor("#349beb")),
    ('BACKGROUND', (0, 1), (0, 1), colors.HexColor("#ed3e46")),
    ('BACKGROUND', (0, 2), (0, 2), colors.HexColor("#eb8034")),
    ('BACKGROUND', (0, 3), (0, 3), colors.HexColor("#9646e0"))]


def createMatrix(test, preguntas, alumnos, matrix, matrixText, respuestasNum):
    try:
        for num, pregunta in enumerate(preguntas):
            question = {}
            if matrixText != 'no':
                questionText = {}
            if respuestasNum != 'no':
                aux = {}
                respuestas = {}
            respuestasPreguntas = db.session.query(Respuesta).join(PreguntasTest,
                                                                   and_(test.id == PreguntasTest.c.test,
                                                                        PreguntasTest.c.pregunta == pregunta.id,
                                                                        Respuesta.c.pregunta == PreguntasTest.c.pregunta, )).all()
            for respuesta in respuestasPreguntas:
                student = db.session.query(AlumnosTest).filter_by(id=respuesta.alumno, test=test.id).one()
                j = json.loads(respuesta.respuesta)
                answers = {}
                if matrixText != 'no':
                    answersText = {}
                if respuestasNum != 'no':
                    resp = {}
                for element in j:
                    if 'text' not in element:
                        if respuestasNum == "no":
                            answers[j.get(element)] = {
                                str('#000000'): str((MIDDLE_POINT - int(element)) + MIDDLE_POINT)}
                        else:
                            resp[j.get(element)] = {str('#ffffff'): str((MIDDLE_POINT - int(element)) + MIDDLE_POINT)}
                            answers[j.get(element)] = (MIDDLE_POINT - int(element)) + MIDDLE_POINT
                        if matrixText != 'no':
                            answersText[j.get(element)] = ''
                    elif matrixText != 'no':
                        for answer in answersText:
                            answersText[answer] = j.get(element)
                for a in alumnos:
                    if respuestasNum == "no":
                        if str(a[1]) == str(student.code) or a[1] not in answers:
                            answers[a[1]] = {str('#000000'): str('')}
                    else:
                        if str(a[1]) == str(student.code) or a[1] not in resp:
                            resp[a[1]] = {str('#ffffff'): str('')}
                            answers[a[1]] = ''
                question[student.code] = answers
                if matrixText != 'no':
                    questionText[student.code] = answersText
                if respuestasNum != "no":
                    # alumnoRespuesta = Alumno.query.get(student.alumno)
                    aux[student.code] = resp
            matrix[num + 1] = question
            if matrixText != 'no':
                matrixText[num + 1] = questionText
            if respuestasNum != "no":
                tipo_pregunta = TipoPregunta.query.get(pregunta.tipo_pregunta)
                respuestas[tipo_pregunta.tipo + ": " + gettext(pregunta.pregunta)] = aux
                if tipo_pregunta.tipo == "PGP":
                    respuestasNum[1] = respuestas
                elif tipo_pregunta.tipo == "PGN":
                    respuestasNum[2] = respuestas
                elif tipo_pregunta.tipo == "PPP":
                    respuestasNum[3] = respuestas
                elif tipo_pregunta.tipo == "PPN":
                    respuestasNum[4] = respuestas
                elif tipo_pregunta.tipo == "AAP":
                    respuestasNum[5] = respuestas
                elif tipo_pregunta.tipo == "AAN":
                    respuestasNum[6] = respuestas
        return
    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)


def get_t(a, inf):
    aAprox = float(round(a, 1))
    if inf:
        if aAprox == 0.0:
            t = -1.64
        elif aAprox == 0.1:
            t = -1.62
        elif aAprox == 0.2:
            t = -1.59
        elif aAprox == 0.3:
            t = -1.56
        elif aAprox == 0.4:
            t = -1.52
        elif aAprox == 0.5:
            t = -1.49
        elif aAprox == 0.6:
            t = -1.46
        elif aAprox == 0.7:
            t = -1.42
        elif aAprox == 0.8:
            t = -1.39
        elif aAprox == 0.9:
            t = -1.35
        elif aAprox == 1.0:
            t = -1.32
        else:
            t = -1.28
    else:
        if aAprox == 0.0:
            t = 1.64
        elif aAprox == 0.1:
            t = 1.67
        elif aAprox == 0.2:
            t = 1.7
        elif aAprox == 0.3:
            t = 1.73
        elif aAprox == 0.4:
            t = 1.75
        elif aAprox == 0.5:
            t = 1.77
        elif aAprox == 0.6:
            t = 1.8
        elif aAprox == 0.7:
            t = 1.82
        elif aAprox == 0.8:
            t = 1.84
        elif aAprox == 0.9:
            t = 1.86
        elif aAprox == 1.0:
            t = 1.88
        else:
            t = 1.89
    return t


def get_soc(sp, sn, ep, en, np, nn):
    if sp[list(sp)[0]] == gettext("Alto") and sn[list(sn)[0]] == gettext("Bajo") and np >= 50:
        pos = gettext("Líder")
    elif sp[list(sp)[0]] == gettext("Alto") and sn[list(sn)[0]] == gettext("Bajo") and np < 50:
        pos = gettext("Astro")
    elif sp[list(sp)[0]] == gettext("Alto") and sn[list(sn)[0]] == gettext("Medio"):
        pos = gettext("Popular")
    elif sp[list(sp)[0]] == gettext("Medio") and (
            sn[list(sn)[0]] == gettext("Medio") or sn[list(sn)[0]] == gettext("Bajo")) and (
            ep[list(ep)[0]] == gettext("Alto") or ep[list(ep)[0]] == gettext("Medio")):
        pos = gettext("Integrado")
    elif sp[list(sp)[0]] == gettext("Medio") and (
            sn[list(sn)[0]] == gettext("Medio") or sn[list(sn)[0]] == gettext("Bajo")) and ep[
        list(ep)[0]] == gettext("Bajo"):
        pos = gettext("Solitario")
    elif sp[list(sp)[0]] == gettext("Alto") and sn[list(sn)[0]] == gettext("Alto"):
        pos = gettext("Polémico")
    elif sp[list(sp)[0]] == gettext("Medio") and sn[list(sn)[0]] == gettext("Alto"):
        pos = gettext("Rechazo Parcial")
    elif sp[list(sp)[0]] == gettext("Bajo") and sn[list(sn)[0]] == gettext("Alto"):
        pos = gettext("Rechazo Total")
    elif sp[list(sp)[0]] == gettext("Bajo") and (
            sn[list(sn)[0]] == gettext("Medio") or sn[list(sn)[0]] == gettext("Bajo")) and ep[
        list(ep)[0]] == gettext("Alto"):
        pos = gettext("Desatendido")
    elif sp[list(sp)[0]] == gettext("Bajo") and (
            sn[list(sn)[0]] == gettext("Medio") or sn[list(sn)[0]] == gettext("Bajo")) and ep[
        list(ep)[0]] == gettext("Medio"):
        pos = gettext("Ignorado")
    elif sp[list(sp)[0]] == gettext("Bajo") and (
            sn[list(sn)[0]] == gettext("Medio") or sn[list(sn)[0]] == gettext("Bajo")) and ep[
        list(ep)[0]] == gettext("Bajo"):
        pos = gettext("Aislado")
    elif sp[list(sp)[0]] == gettext("Bajo") and sn[list(sn)[0]] == gettext("Medio"):
        pos = gettext("Eminencia gris, elegido por el líder")
    else:
        pos = ''
    return pos

def getRecommendations(recommendations, variable, index, indexTitle, innerIndex, innerIndexTitle, lastTitle, URL, etapa, msg, rec, linkName, linkName2, extraRec=None):
    try:
        if lastTitle not in recommendations[variable][index][indexTitle][innerIndex][innerIndexTitle]:
            recommendations[variable][index][indexTitle][innerIndex][innerIndexTitle][lastTitle] = []
            recommendations[variable][index][indexTitle][innerIndex][innerIndexTitle][lastTitle].append(
                URL + etapa + "/" + Link.query.filter_by(name=linkName).one().url + "/" +
                etapa.split('_')[
                    1] + "_" + Link.query.filter_by(name=linkName2).one().url + '.php')
        recommendations[variable][index][indexTitle][innerIndex][innerIndexTitle][lastTitle].append(msg)
        recommendations[variable][index][indexTitle][innerIndex][innerIndexTitle][lastTitle].append(rec)
        if extraRec:
            recommendations[variable][index][indexTitle][innerIndex][innerIndexTitle][lastTitle].append(extraRec)

    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)

def get_proposals(sp, np, nn, sn, spval, snval, imp, ipval, imn, inval, iN, ip, ipp, ipval5, ipn, inval6, data1, data2,
                  data3, data4, n, matrix12, matrix34, matrix, alumnoCurrent, matrixText, grupo_edad, body):
    try:
        spValue, snValue, npValue, nnValue, impValue, imnValue, ipValue, inValue, ipnValue, ippValue, rpValue, rnValue, epValue, ppValue, papValue, enValue, pnValue, panValue = {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}

        for s in spval:
            np[s] = int((float(spval[s]) / ((n - 1) * 5)) * 100)
            nn[s] = int((float(snval[s]) / ((n - 1) * 5)) * 100)

            npValue[s] = escala(2, np[s], 75, 26)
            nnValue[s] = escala(2, nn[s], 75, 26)

            spValue[s] = escala(2, sp[s], data1[7]['Xsup'], data1[8]['Xinf'])
            snValue[s] = escala(2, sn[s], data2[7]['Xsup'], data2[8]['Xinf'])

            imp[s] = int((float(ipval[s]) / ((n - 1) * 5)) * 100)
            imn[s] = int((float(inval[s]) / ((n - 1) * 5)) * 100)

            impValue[s] = escala(2, imp[s], 75, 26)
            imnValue[s] = escala(2, imn[s], 75, 26)

            ipp[s] = int((float(ipval5[s]) / ((n - 1) * 5)) * 100)
            ipn[s] = int((float(inval6[s]) / ((n - 1) * 5)) * 100)

            ippValue[s] = escala(2, ipp[s], 75, 26)
            ipnValue[s] = escala(2, ipn[s], 75, 26)

            ipValue[s] = escala(2, ip[s], data3[7]['Xsup'], data3[8]['Xinf'])
            inValue[s] = escala(2, iN[s], data4[7]['Xsup'], data4[8]['Xinf'])

        ic, id, iap, ian = 0, 0, 0, 0
        for m in matrix12:
            for e in matrix12[m]:
                if (e == "EP" or e == "EN"):
                    matrix12[m][e] = int((float(matrix12[m][e]) / MAX_POINTS) * 100)
                    if e == "EP":
                        epValue[m] = escala(2, matrix12[m][e], 75, 26)
                    else:
                        enValue[m] = escala(2, matrix12[m][e], 75, 26)

                elif e == "RP":
                    ic += matrix12[m][e]
                    if matrix12[m][e] > 0:
                        rpValue[m] = {matrix12[m][e]: "Mayor"}
                    else:
                        rpValue[m] = {matrix12[m][e]: "Cero"}
                elif e == "RN":
                    id += matrix12[m][e]
                    if matrix12[m][e] > 0:
                        rnValue[m] = {matrix12[m][e]: "Mayor"}
                    else:
                        rnValue[m] = {matrix12[m][e]: "Cero"}

        for m in matrix34:
            for e in matrix34[m]:
                if e == "PAP":
                    if matrix34[m]['PP'] != 0:
                        matrix34[m][e] = int((float(matrix34[m][e]) / matrix34[m]['PP']) * 100)
                    else:
                        matrix34[m][e] = 0
                    papValue[m] = escala(2, matrix34[m][e], 75,26)

                elif e == "PAN":
                    if matrix34[m]['PN'] != 0:
                        matrix34[m][e] = int((float(matrix34[m][e]) / matrix34[m]['PN']) * 100)
                    else:
                        matrix34[m][e] = 0
                    panValue[m] = escala(2, matrix34[m][e], 75, 26)

        for m in matrix34:
            for e in matrix34[m]:
                if e == "PP" or e == "PN":
                    matrix34[m][e] = int((float(matrix34[m][e]) / MAX_POINTS) * 100)
                    if e == "PP":
                        ppValue[m] = escala(2, matrix34[m][e], 75, 26)
                    else:
                        pnValue[m] = escala(2, matrix34[m][e], 75, 26)

        ic = int((float(ic) / ((n - 1) * MAX_POINTS)) * 100)
        id = int((float(id) / ((n - 1) * MAX_POINTS)) * 100)
        icValue = escala(3, ic)
        idValue = escala(3, id)


        iap = int((float(sum(sp.values())) / (MAX_POINTS * n)) * 100)
        ian = int((float(sum(sn.values())) / (MAX_POINTS * n)) * 100)
        iapValue = escala(3, iap)
        ianValue = escala(3, ian)


        oipValue = {}
        oinValue = {}
        osValue = {}


        for al in matrix[3]:
            aux = []
            for al2 in matrix[3][al]:
                if "#ed3e46" in matrix[3][al][al2]:
                    aux.append(al2)
            oipValue[al] = aux

        for al in matrix[4]:
            aux = []
            for al2 in matrix[4][al]:
                if "#9646e0" in matrix[4][al][al2]:
                    aux.append(al2)
            oinValue[al] = aux

        for al in matrix[1]:
            aux = {}
            for al2 in matrix[1][al]:
                reasonsOs = ' '
                if "#e05ab8" in matrix[1][al][al2]:
                    if alumnoCurrent != '':
                        o = db.session.query(Alumno, AlumnosTest.c.code, User.nombre, User.apellidos).join(AlumnosTest,
                                                                                                           and_(
                                                                                                               AlumnosTest.c.code == al2,
                                                                                                               AlumnosTest.c.alumno == Alumno.id, )) \
                            .join(User, User.id == Alumno.user).one()
                        if matrixText[2][al2][al] != '':
                            reasonsOs = gettext('Elige a ') + o[2] + " " + o[3] + gettext(
                                ' pero ') + o[2] + " " + o[3] + gettext(
                                ' lo/la rechaza por el motivo "') + matrixText[2][al2][al] + '".'
                        else:
                            reasonsOs = gettext('Elige a ') + o[2] + " " + o[3] + gettext(
                                ' pero ') + o[2] + " " + o[3] + gettext(' lo/la rechaza') + '.'

                    aux[al2] = reasonsOs
            if alumnoCurrent != '':
                for al3 in matrix[2][al]:
                    reasonsOs = ' '
                    if "#e05ab8" in matrix[2][al][al3]:
                        o = db.session.query(Alumno, AlumnosTest.c.code, User.nombre, User.apellidos).join(AlumnosTest,
                                                                                                           and_(
                                                                                                               AlumnosTest.c.code == al3,
                                                                                                               AlumnosTest.c.alumno == Alumno.id, )) \
                            .join(User, User.id == Alumno.user).one()
                        if matrixText[2][al][al3] != '':
                            reasonsOs = gettext('Rechaza a ') + o[2] + " " + o[3] + gettext(
                                ' por el motivo "') + matrixText[2][al][al3] + gettext(
                                '" y ') + o[2] + " " + o[3] + gettext(' lo elige') + '.'
                        else:
                            reasonsOs = gettext('Rechaza a ') + o[2] + " " + o[3] + gettext(
                                ' y ') + o[2] + " " + o[3] + gettext(' lo elige') + '.'

                        aux[al3] = reasonsOs
            osValue[al] = aux

        grupo_edad_name = GrupoEdad.query.get(grupo_edad).grupo_edad
        etapa = Link.query.filter_by(name=grupo_edad_name).one().url
        URL = "https://www.atopa.es/"
        recommendations = {}
        recommendations['IC'] = {1: {gettext('Educación en valores'): {1: {gettext('Interculturalidad'): {}},
                                                                       2: {gettext('Respeto y tolerancia'): {}},
                                                                       3: {gettext('Solidaridad'): {}},
                                                                       4: {gettext('Responsabilidad'): {}}}}, 2: {
            gettext('Grupo y aula'): {1: {gettext('Cohesión de grupo'): {}}, 2: {gettext('Gestión de aula'): {}},
                                      3: {gettext('Trabajo colaborativo y cooperativo'): {}}}}}
        recommendations['ID'] = {1: {gettext('Educación emocional'): {1: {gettext('Autoconcepto y autoestima'): {}},
                                                                      2: {gettext('Autoregulación'): {}},
                                                                      3: {gettext('Habilidades sociales'): {}},
                                                                      4: {gettext('Empatía'): {}},
                                                                      5: {gettext('Resolución de conflictos'): {}}}},
                                 2: {
                                     gettext('Educación en valores'): {1: {gettext('Interculturalidad'): {}},
                                                                       2: {gettext('Solidaridad'): {}}}},
                                 3: {gettext('Grupo y aula'): {1: {gettext('Cohesión de grupo'): {}},
                                                               2: {gettext('Gestión de aula'): {}},
                                                               3: {gettext('Trabajo colaborativo y cooperativo'): {}}}}}
        recommendations['SP'] = {1: {gettext('Educación en valores'): {1: {gettext('Interculturalidad'): {}},
                                                                       2: {gettext('Respeto y tolerancia'): {}},
                                                                       3: {gettext('Solidaridad'): {}},
                                                                       4: {gettext('Responsabilidad'): {}}}}, 2: {
            gettext('Grupo y aula'): {1: {gettext('Cohesión de grupo'): {}}, 2: {gettext('Gestión de aula'): {}},
                                      3: {gettext('Trabajo colaborativo y cooperativo'): {}}}}}
        recommendations['SN'] = {1: {gettext('Educación emocional'): {1: {gettext('Autoconcepto y autoestima'): {}},
                                                                      2: {gettext('Autoregulación'): {}},
                                                                      3: {gettext('Habilidades sociales'): {}},
                                                                      4: {gettext('Empatía'): {}},
                                                                      5: {gettext('Resolución de conflictos'): {}}}},
                                 2: {
                                     gettext('Educación en valores'): {1: {gettext('Interculturalidad'): {}},
                                                                       2: {gettext('Respeto y tolerancia'): {}},
                                                                       3: {gettext('Solidaridad'): {}},
                                                                       4: {gettext('Responsabilidad'): {}}}}}
        recommendations['RP'] = {1: {gettext('Educación emocional'): {1: {gettext('Autoconcepto y autoestima'): {}},
                                                                      2: {gettext('Autoregulación'): {}},
                                                                      3: {gettext('Habilidades sociales'): {}},
                                                                      4: {gettext('Empatía'): {}},
                                                                      5: {gettext('Resolución de conflictos'): {}}}},
                                 2: {
                                     gettext('Grupo y aula'): {1: {gettext('Cohesión de grupo'): {}},
                                                               2: {gettext('Gestión de aula'): {}},
                                                               3: {gettext('Trabajo colaborativo y cooperativo'): {}}}}}
        recommendations['RN'] = {1: {gettext('Educación emocional'): {1: {gettext('Autoconcepto y autoestima'): {}},
                                                                      2: {gettext('Autoregulación'): {}},
                                                                      3: {gettext('Habilidades sociales'): {}},
                                                                      4: {gettext('Empatía'): {}},
                                                                      5: {gettext('Resolución de conflictos'): {}}}},
                                 2: {
                                     gettext('Educación en valores'): {1: {gettext('Interculturalidad'): {}},
                                                                       2: {gettext('Respeto y tolerancia'): {}},
                                                                       3: {gettext('Solidaridad'): {}},
                                                                       4: {gettext('Responsabilidad'): {}}}}}
        recommendations['OS'] = {1: {gettext('Educación emocional'): {1: {gettext('Autoconcepto y autoestima'): {}},
                                                                      2: {gettext('Autoregulación'): {}},
                                                                      3: {gettext('Habilidades sociales'): {}},
                                                                      4: {gettext('Empatía'): {}},
                                                                      5: {gettext('Resolución de conflictos'): {}}}}}
        recommendations['EP'] = {1: {gettext('Educación emocional'): {1: {gettext('Autoconcepto y autoestima'): {}},
                                                                      2: {gettext('Autoregulación'): {}},
                                                                      3: {gettext('Habilidades sociales'): {}},
                                                                      4: {gettext('Empatía'): {}},
                                                                      5: {gettext('Resolución de conflictos'): {}}}},
                                 2: {
                                     gettext('Educación en valores'): {1: {gettext('Interculturalidad'): {}},
                                                                       2: {gettext('Respeto y tolerancia'): {}},
                                                                       3: {gettext('Solidaridad'): {}},
                                                                       4: {gettext('Responsabilidad'): {}}}}, 3: {
                gettext('Grupo y aula'): {1: {gettext('Cohesión de grupo'): {}}, 2: {gettext('Gestión de aula'): {}},
                                          3: {gettext('Trabajo colaborativo y cooperativo'): {}}}}}
        recommendations['PP'] = {1: {gettext('Educación emocional'): {1: {gettext('Autoconcepto y autoestima'): {}},
                                                                      2: {gettext('Autoregulación'): {}},
                                                                      3: {gettext('Habilidades sociales'): {}},
                                                                      4: {gettext('Empatía'): {}},
                                                                      5: {gettext('Resolución de conflictos'): {}}}},
                                 2: {
                                     gettext('Educación en valores'): {1: {gettext('Interculturalidad'): {}},
                                                                       2: {gettext('Respeto y tolerancia'): {}},
                                                                       3: {gettext('Solidaridad'): {}},
                                                                       4: {gettext('Responsabilidad'): {}}}}, 3: {
                gettext('Grupo y aula'): {1: {gettext('Cohesión de grupo'): {}}, 2: {gettext('Gestión de aula'): {}},
                                          3: {gettext('Trabajo colaborativo y cooperativo'): {}}}}}
        recommendations['EN'] = {1: {gettext('Educación emocional'): {1: {gettext('Autoconcepto y autoestima'): {}},
                                                                      2: {gettext('Autoregulación'): {}},
                                                                      3: {gettext('Habilidades sociales'): {}},
                                                                      4: {gettext('Empatía'): {}},
                                                                      5: {gettext('Resolución de conflictos'): {}}}},
                                 2: {
                                     gettext('Educación en valores'): {1: {gettext('Interculturalidad'): {}},
                                                                       2: {gettext('Respeto y tolerancia'): {}},
                                                                       3: {gettext('Solidaridad'): {}},
                                                                       4: {gettext('Responsabilidad'): {}}}}}
        recommendations['PN'] = {1: {gettext('Educación emocional'): {1: {gettext('Autoconcepto y autoestima'): {}},
                                                                      2: {gettext('Autoregulación'): {}},
                                                                      3: {gettext('Habilidades sociales'): {}},
                                                                      4: {gettext('Empatía'): {}},
                                                                      5: {gettext('Resolución de conflictos'): {}}}},
                                 2: {
                                     gettext('Educación en valores'): {1: {gettext('Interculturalidad'): {}},
                                                                       2: {gettext('Respeto y tolerancia'): {}},
                                                                       3: {gettext('Solidaridad'): {}},
                                                                       4: {gettext('Responsabilidad'): {}}}}}

        recommendations['OIP'] = {1: {gettext('Educación emocional'): {1: {gettext('Autoconcepto y autoestima'): {}},
                                                                       2: {gettext('Autoregulación'): {}},
                                                                       3: {gettext('Habilidades sociales'): {}},
                                                                       4: {gettext('Empatía'): {}},
                                                                       5: {gettext('Resolución de conflictos'): {}}}}}
        recommendations['OIN'] = {1: {gettext('Educación emocional'): {1: {gettext('Autoconcepto y autoestima'): {}},
                                                                       2: {gettext('Autoregulación'): {}},
                                                                       3: {gettext('Habilidades sociales'): {}},
                                                                       4: {gettext('Empatía'): {}},
                                                                       5: {gettext('Resolución de conflictos'): {}}}}}
        recommendations['IP'] = {1: {gettext('Educación emocional'): {1: {gettext('Autoconcepto y autoestima'): {}},
                                                                      2: {gettext('Autoregulación'): {}},
                                                                      3: {gettext('Habilidades sociales'): {}},
                                                                      4: {gettext('Empatía'): {}},
                                                                      5: {gettext('Resolución de conflictos'): {}}}}}
        recommendations['IN'] = {1: {gettext('Educación emocional'): {1: {gettext('Autoconcepto y autoestima'): {}},
                                                                      2: {gettext('Autoregulación'): {}},
                                                                      3: {gettext('Habilidades sociales'): {}},
                                                                      4: {gettext('Empatía'): {}},
                                                                      5: {gettext('Resolución de conflictos'): {}}}}}
        recommendations['IPN'] = {1: {gettext('Educación emocional'): {1: {gettext('Autoconcepto y autoestima'): {}},
                                                                       2: {gettext('Autoregulación'): {}},
                                                                       3: {gettext('Habilidades sociales'): {}},
                                                                       4: {gettext('Empatía'): {}},
                                                                       5: {gettext('Resolución de conflictos'): {}}}},
                                  2: {gettext('Educación en valores'): {1: {gettext('Interculturalidad'): {}},
                                                                        2: {gettext('Respeto y tolerancia'): {}},
                                                                        3: {gettext('Solidaridad'): {}},
                                                                        4: {gettext('Responsabilidad'): {}}}}}

        if alumnoCurrent == '':


            if icValue[list(icValue)[0]] == gettext("Bajo"):

                getRecommendations(recommendations, 'IC', 1, gettext('Educación en valores'), 1,
                                   gettext('Interculturalidad'), 'Grupo', URL, etapa,
                                   gettext('El índice de cohesión (IC) del grupo es bajo.'),
                                   gettext(
                                       'Se recomienda trabajar esta categoría en grupos en los que se dé la circunstancia de la multiculturalidad (raza, etnia, religión, etc.).'),
                                   'Educación en valores', 'Interculturalidad')

                getRecommendations(recommendations, 'IC', 1, gettext('Educación en valores'), 3,
                                   gettext('Solidaridad'), 'Grupo', URL, etapa,
                                   gettext('El índice de cohesión (IC) del grupo es bajo.'),
                                   gettext(
                                       'Se recomienda trabajar esta categoría en grupos en los que puedan existir desequilibrios socioeconómicos.'),
                                   'Educación en valores', 'Solidaridad')

                getRecommendations(recommendations, 'IC', 2, gettext('Grupo y aula'), 1,
                                   gettext('Cohesión de grupo'), 'Grupo', URL, etapa,
                                   gettext('El índice de cohesión (IC) del grupo es bajo.'),
                                   gettext(
                                       'Se recomienda trabajar esta categoría en grupos de nueva creación donde los integrantes no se conozcan.'),
                                   'Grupo y aula', 'Cohesión de grupo')

                getRecommendations(recommendations, 'IC', 2, gettext('Grupo y aula'), 3,
                                   gettext('Trabajo colaborativo y cooperativo'), 'Grupo', URL, etapa,
                                   gettext('El índice de cohesión (IC) del grupo es bajo.'),
                                   gettext(
                                       'Se recomienda trabajar esta categoría en grupos donde se observen configuraciones sociométricas de grupos aislados (islas, parejas, triángulos en clique) o cadenas.'),
                                   'Grupo y aula', 'Trabajo colaborativo y cooperativo')

            if idValue[list(idValue)[0]] == gettext("Alto"):

                getRecommendations(recommendations, 'ID', 1, gettext('Educación emocional'), 3,
                                   gettext('Habilidades sociales'), 'Grupo', URL, etapa,
                                   gettext('El índice de disociación (ID) es alto.'),
                                   gettext(
                                       'Se recomienda trabajar esta categoría en grupos donde las respuestas a los rechazos se motiven en actitudes de “falta de educación” “falta de agradecimiento o ayuda” expresado con respuestas tipo “me contesta mal”, “me chincha”, etc.'),
                                   'Educación emocional', 'Habilidades sociales')

                getRecommendations(recommendations, 'ID', 1, gettext('Educación emocional'), 5,
                                   gettext('Resolución de conflictos'), 'Grupo', URL, etapa,
                                   gettext('El índice de disociación (ID) es alto.'),
                                   gettext(
                                       'Se recomienda trabajar esta categoría en grupos donde se observen configuraciones sociométricas de grupos o islas enfrentadas.'),
                                   'Educación emocional', 'Resolución de conflictos')

                getRecommendations(recommendations, 'ID', 2, gettext('Educación en valores'), 1,
                                   gettext('Interculturalidad'), 'Grupo', URL, etapa,
                                   gettext('El índice de disociación (ID) es alto.'),
                                   gettext(
                                       'Se recomienda trabajar esta categoría en grupos en los que se dé la circunstancia de la multiculturalidad (raza, etnia, religión, etc.).'),
                                   'Educación en valores', 'Interculturalidad')

                getRecommendations(recommendations, 'ID', 2, gettext('Educación en valores'), 2,
                                   gettext('Solidaridad'), 'Grupo', URL, etapa,
                                   gettext('El índice de disociación (ID) es alto.'),
                                   gettext(
                                       'Se recomienda trabajar esta categoría en grupos en los que puedan existir desequilibrios socioeconómicos.'),
                                   'Educación en valores', 'Solidaridad')

                getRecommendations(recommendations, 'ID', 3, gettext('Grupo y aula'), 1,
                                   gettext('Cohesión de grupo'), 'Grupo', URL, etapa,
                                   gettext('El índice de disociación (ID) es alto.'),
                                   gettext(
                                       'Se recomienda trabajar esta categoría en grupos donde los rechazos puedan estar motivados por falta de confianza.'),
                                   'Grupo y aula', 'Cohesión de grupo')

                getRecommendations(recommendations, 'ID', 3, gettext('Grupo y aula'), 2,
                                   gettext('Gestión de aula'), 'Grupo', URL, etapa,
                                   gettext('El índice de disociación (ID) es alto.'),
                                   gettext(
                                       'Se recomienda trabajar esta categoría en grupos donde frecuentemente se justifiquen los rechazos en conductas molestas por parte de los compañeros o compañeras, falta de respeto a las normas, turnos de palabra, etc.'),
                                   'Grupo y aula', 'Gestión de aula')


                getRecommendations(recommendations, 'ID', 3, gettext('Grupo y aula'), 3,
                                   gettext('Trabajo colaborativo y cooperativo'), 'Grupo', URL, etapa,
                                   gettext('El índice de disociación (ID) es alto.'),
                                   gettext(
                                       'Se recomienda trabajar esta categoría en grupos donde se observen configuraciones sociométricas de grupos enfrentados.'),
                                   'Grupo y aula', 'Trabajo colaborativo y cooperativo')



            if icValue[list(icValue)[0]] == gettext("Muy bajo") and iapValue[list(iapValue)[0]] == gettext("Muy bajo"):

                getRecommendations(recommendations, 'IC', 1, gettext('Educación en valores'), 1,
                                   gettext('Interculturalidad'), 'Grupo', URL, etapa,
                                   gettext('El índice de cohesión (IC) y el de actividad positiva (IAP) del grupo son muy bajos.'),
                                   gettext(
                                       'Se recomienda trabajar esta categoría en grupos en los que se dé la circunstancia de la multiculturalidad (raza, etnia, religión, etc.).'),
                                   'Educación en valores', 'Interculturalidad')

                getRecommendations(recommendations, 'IC', 1, gettext('Educación en valores'), 3,
                                   gettext('Solidaridad'), 'Grupo', URL, etapa,
                                   gettext(
                                       'El índice de cohesión (IC) y el de actividad positiva (IAP) del grupo son muy bajos.'),
                                   gettext(
                                       'Se recomienda trabajar esta categoría en grupos en los que puedan existir desequilibrios socioeconómicos.'),
                                   'Educación en valores', 'Solidaridad')

                getRecommendations(recommendations, 'IC', 2, gettext('Grupo y aula'), 1,
                                   gettext('Cohesión de grupo'), 'Grupo', URL, etapa,
                                   gettext(
                                       'El índice de cohesión (IC) y el de actividad positiva (IAP) del grupo son muy bajos.'),
                                   gettext(
                                       'Se recomienda trabajar esta categoría en grupos de nueva creación donde los integrantes no se conozcan.'),
                                   'Grupo y aula', 'Cohesión de grupo')

                getRecommendations(recommendations, 'IC', 2, gettext('Grupo y aula'), 3,
                                   gettext('Trabajo colaborativo y cooperativo'), 'Grupo', URL, etapa,
                                   gettext(
                                       'El índice de cohesión (IC) y el de actividad positiva (IAP) del grupo son muy bajos.'),
                                   gettext(
                                       'Se recomienda trabajar esta categoría en grupos donde se observen configuraciones sociométricas de grupos aislados (islas, parejas, triángulos en clique) o cadenas.'),
                                   'Grupo y aula', 'Trabajo colaborativo y cooperativo')

            if idValue[list(idValue)[0]] == gettext("Muy alto") and ianValue[list(ianValue)[0]] == gettext("Muy alto"):

                    getRecommendations(recommendations, 'ID', 1, gettext('Educación emocional'), 3,
                                       gettext('Habilidades sociales'), 'Grupo', URL, etapa,
                                       gettext(
                                           'El índice de disociación (ID) y el de actividad negativa (IAN) son muy altos.'),
                                       gettext(
                                           'Se recomienda trabajar esta categoría en grupos donde las respuestas a los rechazos se motiven en actitudes de “falta de educación” “falta de agradecimiento o ayuda” expresado con respuestas tipo “me contesta mal”, “me chincha”, etc.'),
                                       'Educación emocional', 'Habilidades sociales')

                    getRecommendations(recommendations, 'ID', 1, gettext('Educación emocional'), 5,
                                       gettext('Resolución de conflictos'), 'Grupo', URL, etapa,
                                       gettext(
                                           'El índice de disociación (ID) y el de actividad negativa (IAN) son muy altos.'),
                                       gettext(
                                           'Se recomienda trabajar esta categoría en grupos donde se observen configuraciones sociométricas de grupos o islas enfrentadas.'),
                                       'Educación emocional', 'Resolución de conflictos')

                    getRecommendations(recommendations, 'ID', 2, gettext('Educación en valores'), 1,
                                       gettext('Interculturalidad'), 'Grupo', URL, etapa,
                                       gettext(
                                           'El índice de disociación (ID) y el de actividad negativa (IAN) son muy altos.'),
                                       gettext(
                                           'Se recomienda trabajar esta categoría en grupos en los que se dé la circunstancia de la multiculturalidad (raza, etnia, religión, etc.).'),
                                       'Educación en valores', 'Interculturalidad')

                    getRecommendations(recommendations, 'ID', 2, gettext('Educación en valores'), 2,
                                       gettext('Solidaridad'), 'Grupo', URL, etapa,
                                       gettext(
                                           'El índice de disociación (ID) y el de actividad negativa (IAN) son muy altos.'),
                                       gettext(
                                           'Se recomienda trabajar esta categoría en grupos en los que puedan existir desequilibrios socioeconómicos.'),
                                       'Educación en valores', 'Solidaridad')

                    getRecommendations(recommendations, 'ID', 3, gettext('Grupo y aula'), 1,
                                       gettext('Cohesión de grupo'), 'Grupo', URL, etapa,
                                       gettext(
                                           'El índice de disociación (ID) y el de actividad negativa (IAN) son muy altos.'),
                                       gettext(
                                           'Se recomienda trabajar esta categoría en grupos donde los rechazos puedan estar motivados por falta de confianza.'),
                                       'Grupo y aula', 'Cohesión de grupo')

                    getRecommendations(recommendations, 'ID', 3, gettext('Grupo y aula'), 2,
                                       gettext('Gestión de aula'), 'Grupo', URL, etapa,
                                       gettext(
                                           'El índice de disociación (ID) y el de actividad negativa (IAN) son muy altos.'),
                                       gettext(
                                           'Se recomienda trabajar esta categoría en grupos en los que frecuentemente se justifiquen los rechazos en conductas molestas por parte de los compañeros o compañeras, falta de respeto a las normas, turnos de palabra, etc.'),
                                       'Grupo y aula', 'Gestión de aula')

                    getRecommendations(recommendations, 'ID', 3, gettext('Grupo y aula'), 3,
                                       gettext('Trabajo colaborativo y cooperativo'), 'Grupo', URL, etapa,
                                       gettext(
                                           'El índice de disociación (ID) y el de actividad negativa (IAN) son muy altos.'),
                                       gettext(
                                           'Se recomienda trabajar esta categoría en grupos donde se observen configuraciones sociométricas de grupos enfrentados.'),
                                       'Grupo y aula', 'Trabajo colaborativo y cooperativo')

        if alumnoCurrent != '':
            spValue = {alumnoCurrent: spValue[alumnoCurrent]}

        othersDone = {}

        for user in spValue:
            studentName = db.session.query(Alumno, AlumnosTest.c.code, User.nombre, User.apellidos).join(AlumnosTest,
                                                                                                         and_(
                                                                                                             AlumnosTest.c.code == user,
                                                                                                             AlumnosTest.c.alumno == Alumno.id, )) \
                                                                                                    .join(User, User.id == Alumno.user).one()

            if spValue[user][list(spValue[user])[0]] == gettext("Bajo") and npValue[user][list(npValue[user])[0]] == gettext("Bajo"):

                getRecommendations(recommendations, 'SP', 1, gettext('Educación en valores'), 1,
                                   gettext('Interculturalidad'), gettext("Entre ") + studentName[2] + " " + studentName[3] + gettext(" y el grupo "), URL, etapa,
                                   gettext('Su estatus de elecciones positivas (SP) y su nivel medio de popularidad (NP) son bajos.'),
                                   gettext(
                                       'Cuando se dé la circunstancia de la multiculturalidad (raza, etnia, religión, etc.)'),
                                   'Educación en valores', 'Interculturalidad')

                getRecommendations(recommendations, 'SP', 1, gettext('Educación en valores'), 2,
                                   gettext('Respeto y tolerancia'),
                                   gettext("Entre ") + studentName[2] + " " + studentName[3] + gettext(" y el grupo "),
                                   URL, etapa,
                                   gettext(
                                       'Su estatus de elecciones positivas (SP) y su nivel medio de popularidad (NP) son bajos.'),
                                   gettext(
                                       'Cuando se den las circunstancias de diversidad funcional o singularidad física o psíquica, identidad de género, diferencias socioeconómicas, etc.'),
                                   'Educación en valores', 'Respeto y tolerancia')

            if user in ppValue and user in papValue:
                if ppValue[user][list(ppValue[user])[0]] == gettext("Bajo") and papValue[user][list(papValue[user])[0]] == gettext("Alto"):

                    getRecommendations(recommendations, 'PP', 3, gettext('Grupo y aula'), 1,
                                       gettext('Cohesión de grupo'),
                                       gettext("Entre ") + studentName[2] + " " + studentName[3] + gettext(
                                           " y el grupo "),
                                       URL, etapa,
                                       gettext(
                                           'El número de compañeros por los que se cree elegido (PP) es bajo y su percepción acertada de ese número (PAP) es alta.'),
                                       gettext(
                                           'Se dé la circunstancia de ser un alumno de nueva incorporación o desconocido para el grupo.'),
                                       'Grupo y aula', 'Cohesión de grupo')

                    getRecommendations(recommendations, 'PP', 3, gettext('Grupo y aula'), 3,
                                       gettext('Trabajo colaborativo y cooperativo'),
                                       gettext("Entre ") + studentName[2] + " " + studentName[3] + gettext(
                                           " y el grupo "),
                                       URL, etapa,
                                       gettext(
                                           'El número de compañeros por los que se cree elegido (PP) es bajo y su percepción acertada de ese número (PAP) es alta.'),
                                       '',
                                       'Grupo y aula', 'Trabajo colaborativo y cooperativo')

                    getRecommendations(recommendations, 'PP', 2, gettext('Educación en valores'), 4,
                                       gettext('Responsabilidad'),
                                       studentName[2] + " " + studentName[3],
                                       URL, etapa,
                                       gettext(
                                           'El número de compañeros por los que se cree elegido (PP) es bajo y su percepción acertada de ese número (PAP) es alta.'),
                                       '',
                                       'Educación en valores', 'Responsabilidad')


                if ppValue[user][list(ppValue[user])[0]] == gettext("Bajo") and papValue[user][list(papValue[user])[0]] == gettext("Bajo"):

                    getRecommendations(recommendations, 'PP', 1, gettext('Educación emocional'), 1,
                                       gettext('Autoconcepto y autoestima'),
                                       studentName[2] + " " + studentName[3],
                                       URL, etapa,
                                       gettext(
                                           'El número de compañeros por los que se cree elegido (PP) es bajo y su percepción acertada de ese número (PAP) es baja.'),
                                       '',
                                       'Educación emocional', 'Autoconcepto y autoestima')

            if user in rpValue:
                if rpValue[user][list(rpValue[user])[0]] == "Cero":

                    getRecommendations(recommendations, 'RP', 1, gettext('Educación emocional'), 1,
                                       gettext('Autoconcepto y autoestima'),
                                       studentName[2] + " " + studentName[3],
                                       URL, etapa,
                                       gettext(
                                           'No tiene elecciones recíprocas positivas (RP) o amistades.'),
                                       gettext('Cuando un alumno no tiene amistades (RP) se debe potenciar las cualidades positivas del alumno en el grupo.'),
                                       'Educación emocional', 'Autoconcepto y autoestima')

                    getRecommendations(recommendations, 'RP', 2, gettext('Grupo y aula'), 1,
                                       gettext('Cohesión de grupo'),
                                       studentName[2] + " " + studentName[3],
                                       URL, etapa,
                                       gettext(
                                           'No tiene elecciones recíprocas positivas (RP) o amistades.'),
                                       gettext('Cuando un alumno no tiene amistades (RP) y se dé la circunstancia de ser un alumno de nueva incorporación o tenga una personalidad introvertida, puede tener una posición sociométrica de aislado o marginado.'),
                                       'Grupo y aula', 'Cohesión de grupo')

            if user in pnValue and user in panValue:
                if pnValue[user][list(pnValue[user])[0]] == gettext("Alto") and panValue[user][list(panValue[user])[0]] == gettext("Bajo"):

                    getRecommendations(recommendations, 'PN', 1, gettext('Educación emocional'), 1,
                                       gettext('Autoconcepto y autoestima'),
                                       studentName[2] + " " + studentName[3],
                                       URL, etapa,
                                       gettext(
                                           'El número de compañeros por los que se cree rechazado o percepción negativa (PN) es alta y su percepción acertada de ese número (PAN) es baja.'),
                                       '',
                                       'Educación emocional', 'Autoconcepto y autoestima')


                if pnValue[user][list(pnValue[user])[0]] == gettext("Alto") and panValue[user][list(panValue[user])[0]] == gettext("Alto"):

                    getRecommendations(recommendations, 'PN', 1, gettext('Educación emocional'), 2,
                                       gettext('Autoregulación'),
                                       studentName[2] + " " + studentName[3],
                                       URL, etapa,
                                       gettext(
                                           'El número de compañeros por los que se cree rechazado o percepción negativa (PN) es alta y su percepción acertada de ese número (PAN) es alta, motivado en cuestiones de conducta molesta.'),
                                       '',
                                       'Educación emocional', 'Autoregulación')

            if ipnValue[user][list(ipnValue[user])[0]] == gettext("Alto"):

                getRecommendations(recommendations, 'IPN', 1, gettext('Educación emocional'), 1,
                                   gettext('Autoconcepto y autoestima'),
                                   studentName[2] + " " + studentName[3],
                                   URL, etapa,
                                   gettext(
                                       'La cantidad de veces que es nombrado/a por sus compañeros en las categorías de carácter negativo o el índice de preferencia social negativa (IPN) es alto.'),
                                   gettext('Cuando el índice afecta al atributo de "triste" o similar.'),
                                   'Educación emocional', 'Autoconcepto y autoestima')

                getRecommendations(recommendations, 'IPN', 1, gettext('Educación emocional'), 2,
                                   gettext('Autoregulación'),
                                   studentName[2] + " " + studentName[3],
                                   URL, etapa,
                                   gettext(
                                       'La cantidad de veces que es nombrado/a por sus compañeros en las categorías de carácter negativo o el índice de preferencia social negativa (IPN) es alto.'),
                                   gettext('Cuando el índice afecta al atributo de "molestar" o similar.'),
                                   'Educación emocional', 'Autoregulación')

                getRecommendations(recommendations, 'IPN', 1, gettext('Educación emocional'), 3,
                                   gettext('Habilidades sociales'),
                                   studentName[2] + " " + studentName[3],
                                   URL, etapa,
                                   gettext(
                                       'La cantidad de veces que es nombrado/a por sus compañeros en las categorías de carácter negativo o el índice de preferencia social negativa (IPN) es alto.'),
                                   gettext('Cuando el índice afecta al atributo de "pesado" o similar.'),
                                   'Educación emocional', 'Habilidades sociales')

            if snValue[user][list(snValue[user])[0]] == gettext("Alto") and nnValue[user][list(nnValue[user])[0]] == gettext("Alto"):

                getRecommendations(recommendations, 'SN', 1, gettext('Educación emocional'), 2,
                                   gettext('Autoregulación'),
                                   studentName[2] + " " + studentName[3],
                                   URL, etapa,
                                   gettext(
                                       'Su estatus de eleccions negativas (SN) y su nivel medio de rechazo (NN) son altos'),
                                   gettext('Alumnado con posiciones sociométricas de rechazado parcial o total y con índice de rechazo (SN) alto en el que las respuestas al “por qué” del rechazo sean similares a “porque me molesta”  y cuestiones de molestia acerca de su conducta.'),
                                   'Educación emocional', 'Autoregulación')

            if ipValue[user][list(ipValue[user])[0]] == gettext("Bajo") and impValue[user][list(impValue[user])[0]] == gettext("Bajo"):

                getRecommendations(recommendations, 'IP', 1, gettext('Educación emocional'), 3,
                                   gettext('Habilidades sociales'),
                                   studentName[2] + " " + studentName[3],
                                   URL, etapa,
                                   gettext(
                                       'El número de compañeros que se creen elegidos por él/ella o su impresión positiva (IP) es baja y el nivel medio de impresión que tiene el grupo de ser elegido por él/ella (IMP) es bajo'),
                                   gettext('El grupo no se cree escogido por el alumno o alumna.'),
                                   'Educación emocional', 'Habilidades sociales')

            if user in oinValue:
                if len(oinValue[user]) > 0:
                    otherStudents = ''
                    reasons = ''
                    if len(oinValue[user]) > 0:
                        for r in oinValue[user]:
                            o = db.session.query(Alumno, AlumnosTest.c.code, User.nombre, User.apellidos).join(
                                AlumnosTest,
                                and_(
                                    AlumnosTest.c.code == r,
                                    AlumnosTest.c.alumno == Alumno.id, )) \
                                .join(User, User.id == Alumno.user).one()
                            if otherStudents == '':
                                otherStudents += o[2] + " " + o[3]
                            else:
                                otherStudents += "/" + o[2] + " " + o[3]
                            if alumnoCurrent != '':
                                reasons += o[2] + " " + o[3] + gettext(' lo/la elige')
                        if otherStudents != '':

                            getRecommendations(recommendations, 'OIN', 1, gettext('Educación emocional'), 1,
                                               gettext('Autoconcepto y autoestima'),
                                               studentName[2] + " " + studentName[3],
                                               URL, etapa,
                                               gettext(
                                                   'Contradicción entre la expectativa de ser rechazado por determinados compañeros o compañeras cuando en realidad han sido elegidos por ellos'),
                                               reasons + gettext(" cuando el pensaba ser rechazado/a."),
                                               'Educación emocional', 'Autoconcepto y autoestima')

            if user in epValue:
                if epValue[user][list(epValue[user])[0]] == gettext("Bajo"):

                    getRecommendations(recommendations, 'EP', 1, gettext('Educación emocional'), 4,
                                       gettext('Empatía'),
                                       gettext("Entre ") + studentName[2] + " " + studentName[3] + gettext(
                                           " y el grupo "),
                                       URL, etapa,
                                       gettext(
                                           'La suma de sus elecciones positivas o expansividad positiva (EP) es baja'),
                                       gettext(
                                           'Puede tener una posición sociométrica de solitario.'),
                                       'Educación emocional', 'Empatía')

                    getRecommendations(recommendations, 'EP', 2, gettext('Educación en valores'), 2,
                                       gettext('Respeto y tolerancia'),
                                       gettext("Entre ") + studentName[2] + " " + studentName[3] + gettext(
                                           " y el grupo "),
                                       URL, etapa,
                                       gettext(
                                           'La suma de sus elecciones positivas o expansividad positiva (EP) es baja'),
                                       gettext(
                                           'Si se dan las circunstancias de diversidad funcional o singularidad física o psíquica, identidad de género, diferencias socioeconómicas, etc. en él o en su entorno.'),
                                       'Educación en valores', 'Respeto y tolerancia')

                    getRecommendations(recommendations, 'EP', 3, gettext('Grupo y aula'), 1,
                                       gettext('Cohesión de grupo'),
                                       gettext("Entre ") + studentName[2] + " " + studentName[3] + gettext(
                                           " y el grupo "),
                                       URL, etapa,
                                       gettext(
                                           'La suma de sus elecciones positivas o expansividad positiva (EP) es baja'),
                                       gettext(
                                           'Si se da la circunstancia de ser un alumno de nueva incorporación.'),
                                       'Grupo y aula', 'Cohesión de grupo')

                    getRecommendations(recommendations, 'EP', 3, gettext('Grupo y aula'), 3,
                                       gettext('Trabajo colaborativo y cooperativo'),
                                       gettext("Entre ") + studentName[2] + " " + studentName[3] + gettext(
                                           " y el grupo "),
                                       URL, etapa,
                                       gettext(
                                           'La suma de sus elecciones positivas o expansividad positiva (EP) es baja'),
                                       '',
                                       'Grupo y aula', 'Trabajo colaborativo y cooperativo')

            if user in enValue:
                otherStudents = ''
                reasons = ''
                if enValue[user][list(enValue[user])[0]] == gettext("Alto"):
                    for r in matrix[2][user]:
                        o = db.session.query(Alumno, AlumnosTest.c.code, User.nombre, User.apellidos).join(AlumnosTest,
                                                                                                           and_(
                                                                                                               AlumnosTest.c.code == r,
                                                                                                               AlumnosTest.c.alumno == Alumno.id, )) \
                            .join(User, User.id == Alumno.user).one()
                        if list(matrix[2][user][r].values())[0] != '':
                            if otherStudents == '':
                                otherStudents += o[2] + " " + o[3]
                            else:
                                otherStudents += "/" + o[2] + " " + o[3]
                        if alumnoCurrent != '':
                            if r in matrixText[2][user]:
                                if matrixText[2][user][r] != '':
                                    reasons += gettext('Rechaza a ') + o[2] + " " + o[3] + gettext(
                                        ' por el motivo "') + matrixText[2][user][r] + '". '
                                else:
                                    reasons += gettext('Rechaza a ') + o[2] + " " + o[3] + '. '
                    if otherStudents != '':

                        getRecommendations(recommendations, 'EN', 1, gettext('Educación emocional'), 4,
                                           gettext('Empatía'),
                                           gettext("Entre ") + studentName[2] + " " + studentName[3] + gettext(
                                               " y ") + otherStudents,
                                           URL, etapa,
                                           gettext(
                                               'La suma de sus elecciones negativas o su expansividad negativa (EN) es alta.'),
                                           reasons,
                                           'Educación emocional', 'Empatía')

                        getRecommendations(recommendations, 'EN', 2, gettext('Educación en valores'), 2,
                                           gettext('Respeto y tolerancia'),
                                           gettext("Entre ") + studentName[2] + " " + studentName[3] + gettext(
                                               " y ") + otherStudents,
                                           URL, etapa,
                                           gettext(
                                               'La suma de sus elecciones negativas o su expansividad negativa (EN) es alta.'),
                                           reasons,
                                           'Educación en valores', 'Respeto y tolerancia', gettext('Si se dan las circunstancias de diversidad funcional o singularidad física o psíquica, identidad de género, diferencias socioeconómicas, etc. en él o en su entorno.'))


            otherStudents = ''
            reasons = ''
            if inValue[user][list(inValue[user])[0]] == gettext("Alto") and imnValue[user][
                list(imnValue[user])[0]] == gettext("Alto"):
                for r in matrix[4]:
                    if user in matrix[4][r]:
                        o = db.session.query(Alumno, AlumnosTest.c.code, User.nombre, User.apellidos).join(AlumnosTest,
                                                                                                           and_(
                                                                                                               AlumnosTest.c.code == r,
                                                                                                               AlumnosTest.c.alumno == Alumno.id, )) \
                            .join(User, User.id == Alumno.user).one()
                        if list(matrix[4][user][r].values())[0] != '':
                            if otherStudents == '':
                                otherStudents += o[2] + " " + o[3]
                            else:
                                otherStudents += "/" + o[2] + " " + o[3]
                        if alumnoCurrent != '':
                            if user in matrixText[4][r]:
                                if matrixText[4][r][user] != '':
                                    reasons += o[2] + " " + o[3] + gettext(
                                        ' piensa que lo/la rechaza por el motivo "') + matrixText[4][r][user] + '". '
                                else:
                                    reasons += o[2] + " " + o[3] + gettext(
                                        ' piensa que lo/la rechaza') + '. '
                if otherStudents != '':

                    getRecommendations(recommendations, 'IN', 1, gettext('Educación emocional'), 3,
                                       gettext('Habilidades sociales'),
                                       gettext("Entre ") + studentName[2] + " " + studentName[3] + gettext(
                                           " y ") + otherStudents,
                                       URL, etapa,
                                       gettext(
                                           'El número de compañeros que se creen rechazados por él/ella o su impresión negativa (IN) es alta y el nivel medio de impresión que tiene el grupo de ser rechazado por él/ella (IMN) es alto.'),
                                       reasons,
                                       'Educación emocional', 'Habilidades sociales')

            if user in osValue:
                if len(osValue[user]) > 0:
                    for r in osValue[user]:
                        o = db.session.query(Alumno, AlumnosTest.c.code, User.nombre, User.apellidos).join(AlumnosTest,
                                                                                                           and_(
                                                                                                               AlumnosTest.c.code == r,
                                                                                                               AlumnosTest.c.alumno == Alumno.id, )) \
                            .join(User, User.id == Alumno.user).one()

                        getRecommendations(recommendations, 'OS', 1, gettext('Educación emocional'), 3,
                                           gettext('Habilidades sociales'),
                                           gettext("Entre ") + studentName[2] + " " + studentName[3] + gettext(
                                               " y ") + o[2] + " " + o[3],
                                           URL, etapa,
                                           gettext(
                                               'Tienen oposición de sentimientos (OS) de tal forma que un alumno o alumna escoge a otro que lo rechaza.'),
                                           reasons,
                                           'Educación emocional', 'Habilidades sociales')

                        getRecommendations(recommendations, 'OS', 1, gettext('Educación emocional'), 4,
                                           gettext('Empatía'),
                                           gettext("Entre ") + studentName[2] + " " + studentName[3] + gettext(
                                               " y ") + o[2] + " " + o[3],
                                           URL, etapa,
                                           gettext(
                                               'Tienen oposición de sentimientos (OS) de tal forma que un alumno o alumna escoge a otro que lo rechaza.'),
                                           osValue[user][r],
                                           'Educación emocional', 'Empatía')




            if user in oipValue:
                otherStudents = ''
                reasons = ''
                if len(oipValue[user]) > 0:
                    for r in oipValue[user]:
                        o = db.session.query(Alumno, AlumnosTest.c.code, User.nombre, User.apellidos).join(AlumnosTest,
                                                                                                           and_(
                                                                                                               AlumnosTest.c.code == r,
                                                                                                               AlumnosTest.c.alumno == Alumno.id, )) \
                            .join(User, User.id == Alumno.user).one()
                        if otherStudents == '':
                            otherStudents += o[2] + " " + o[3]
                        else:
                            otherStudents += "/" + o[2] + " " + o[3]
                        if alumnoCurrent != '':
                            if user in matrixText[2][r]:
                                if matrixText[2][r][user] != '':
                                    reasons += o[2] + " " + o[3] + gettext(
                                        ' lo/la rechaza por el motivo "') + matrixText[2][r][user]
                                else:
                                    reasons += o[2] + " " + o[3] + gettext(' lo/la rechaza')
                    if otherStudents != '':

                        getRecommendations(recommendations, 'OIP', 1, gettext('Educación emocional'), 3,
                                           gettext('Habilidades sociales'),
                                           gettext("Entre ") + studentName[2] + " " + studentName[3] + gettext(
                                               " y ") + otherStudents,
                                           URL, etapa,
                                           gettext(
                                               'Contradicción entre la expectativa de ser elegido por determinados compañeros o compañeras cuando en realidad han sido rechazados por ellos.'),
                                           reasons + gettext(" cuando pensaba ser elegido/a."),
                                           'Educación emocional', 'Habilidades sociales')

            if user in rnValue:
                if rnValue[user][list(rnValue[user])[0]] == "Mayor":
                    others = ''
                    reasons = ''
                    for r in matrix[2][user]:
                        if "#0da863" in matrix[2][user][r]:
                            o = db.session.query(Alumno, AlumnosTest.c.code, User.nombre, User.apellidos).join(
                                AlumnosTest,
                                and_(
                                    AlumnosTest.c.code == r,
                                    AlumnosTest.c.alumno == Alumno.id, )) \
                                .join(User, User.id == Alumno.user).one()
                            if others == '' and (str(r) + str(user)) not in othersDone:
                                others += o[2] + " " + o[3]
                                othersDone[str(user) + str(r)] = True
                            elif (str(r) + str(user)) not in othersDone:
                                others += "/" + o[2] + " " + o[3]
                            if alumnoCurrent != '':
                                if r in matrixText[2][user] and user in matrixText[2][r]:
                                    if matrixText[2][user][r] != '' and matrixText[2][r][user] != '':
                                        reasons += gettext(
                                            'Rechaza a ') + o[2] + " " + o[3] + gettext(
                                            ' por el motivo "') + matrixText[2][user][r] + gettext(
                                            '" y ') + o[2] + " " + o[3] + gettext(
                                            ' lo/la rechaza por el motivo "') + matrixText[2][r][user] + '". '
                                    elif matrixText[2][user][r] != '':
                                        reasons += gettext(
                                            'Rechaza a ') + o[2] + " " + o[3] + gettext(
                                            ' por el motivo "') + matrixText[2][user][r] + gettext(
                                            '" y ') + o[2] + " " + o[3] + gettext(
                                            ' lo/la rechaza') + '. '
                                    elif matrixText[2][r][user] != '':
                                        reasons += gettext(
                                            'Rechaza a ') + o[2] + " " + o[3] + gettext(
                                            ' y ') + o[2] + " " + o[3] + gettext(
                                            ' lo/la rechaza por el motivo "') + matrixText[2][r][user] + '". '
                                    else:
                                        reasons += gettext(
                                            'Rechaza a ') + o[2] + " " + o[3] + gettext(
                                            ' y ') + o[2] + " " + o[3] + gettext(
                                            ' lo/la rechaza') + '. '
                    if others != '':

                        getRecommendations(recommendations, 'RN', 1, gettext('Educación emocional'), 5,
                                           gettext('Resolución de conflictos'),
                                           gettext("Entre ") + studentName[2] + " " + studentName[3] + gettext(
                                               " y ") + others,
                                           URL, etapa,
                                           gettext(
                                               'Existe enemistad o rechazos recíprocos (RN) entre ellos.'),
                                           reasons,
                                           'Educación emocional', 'Resolución de conflictos')

                        getRecommendations(recommendations, 'RN', 2, gettext('Educación en valores'), 2,
                                           gettext('Respeto y tolerancia'),
                                           gettext("Entre ") + studentName[2] + " " + studentName[3] + gettext(
                                               " y ") + others,
                                           URL, etapa,
                                           gettext(
                                               'Cuando existan enemistad o rechazos recíprocos (RN) entre ellos y cuando se den las circunstancias de diversidad funcional o singularidad física o psíquica, identidad de género, diferencias socioeconómicas, etc.'),
                                           reasons,
                                           'Educación en valores', 'Respeto y tolerancia')

            otherStudents = ''
            reasons = ''
            if snValue[user][list(snValue[user])[0]] == gettext("Alto") and nnValue[user][
                list(nnValue[user])[0]] == gettext("Alto"):
                for r in matrix[2][user]:
                    o = db.session.query(Alumno, AlumnosTest.c.code, User.nombre, User.apellidos).join(AlumnosTest,
                                                                                                       and_(
                                                                                                           AlumnosTest.c.code == r,
                                                                                                           AlumnosTest.c.alumno == Alumno.id, )) \
                        .join(User, User.id == Alumno.user).one()
                    if list(matrix[2][user][r].values())[0] != '':
                        if otherStudents == '':
                            otherStudents += o[2] + " " + o[3]
                        else:
                            otherStudents += "/" + o[2] + " " + o[3]
                    if alumnoCurrent != '':
                        if r in matrixText[2][user]:
                            if matrixText[2][user][r] != '':
                                reasons += gettext('Rechaza a ') + o[2] + " " + o[3] + gettext(
                                    ' por el motivo "') + matrixText[2][user][r] + '". '
                            else:
                                reasons += gettext('Rechaza a ') + o[2] + " " + o[3] + '. '
                if otherStudents != '':

                    getRecommendations(recommendations, 'SN', 2, gettext('Educación en valores'), 1,
                                       gettext('Interculturalidad'),
                                       gettext("Entre ") + studentName[2] + " " + studentName[3] + gettext(
                                           " y ") + otherStudents,
                                       URL, etapa,
                                       gettext(
                                           'Su estatus de eleccions negativas (SN) y su nivel medio de rechazo (NN) son altos.'),
                                       reasons,
                                       'Educación en valores', 'Interculturalidad', gettext(
                            'Cuando se dé la circunstancia de la multiculturalidad (raza, etnia, religión, etc.).'))

                    getRecommendations(recommendations, 'SN', 2, gettext('Educación en valores'), 2,
                                       gettext('Respeto y tolerancia'),
                                       gettext("Entre ") + studentName[2] + " " + studentName[3] + gettext(
                                           " y ") + otherStudents,
                                       URL, etapa,
                                       gettext(
                                           'Su estatus de eleccions negativas (SN) y su nivel medio de rechazo (NN) son altos.'),
                                       reasons,
                                       'Educación en valores', 'Respeto y tolerancia', gettext('Cuando se den las circunstancias de diversidad funcional o singularidad física o psíquica, identidad de género, diferencias socioeconómicas, etc.'))

                    getRecommendations(recommendations, 'SN', 2, gettext('Educación en valores'), 4,
                                       gettext('Responsabilidad'),
                                       gettext("Entre ") + studentName[2] + " " + studentName[3] + gettext(
                                           " y ") + otherStudents,
                                       URL, etapa,
                                       gettext(
                                           'Su estatus de eleccions negativas (SN) y su nivel medio de rechazo (NN) son altos.'),
                                       reasons,
                                       'Educación en valores', 'Responsabilidad', gettext(
                            'En preguntas de ámbito formal en las que las justificaciones de los rechazos se basen en que determinado alumno o alumna no realiza su parte de trabajo de grupo.'))

            if user in pnValue and user in panValue:
                otherStudents = ''
                reasons = ''
                if pnValue[user][list(pnValue[user])[0]] == gettext("Alto") and panValue[user][
                    list(panValue[user])[0]] == gettext("Alto"):
                    for r in matrix[4][user]:
                        o = db.session.query(Alumno, AlumnosTest.c.code, User.nombre, User.apellidos).join(AlumnosTest,
                                                                                                           and_(
                                                                                                               AlumnosTest.c.code == r,
                                                                                                               AlumnosTest.c.alumno == Alumno.id, )) \
                            .join(User, User.id == Alumno.user).one()
                        if list(matrix[4][user][r].values())[0] != '':
                            if otherStudents == '':
                                otherStudents += o[2] + " " + o[3]
                            else:
                                otherStudents += "/" + o[2] + " " + o[3]
                        if alumnoCurrent != '':
                            if r in matrixText[4][user]:
                                if matrixText[4][user][r] != '':
                                    reasons += gettext('Piensa que') + o[2] + " " + o[3] + gettext(
                                        ' lo/la rechaza por el motivo "') + matrixText[4][user][r] + '". '
                                else:
                                    reasons += gettext('Piensa que') + o[2] + " " + o[3] + gettext(
                                        ' lo/la rechaza') + '. '

                    if otherStudents != '':

                        getRecommendations(recommendations, 'PN', 2, gettext('Educación en valores'), 1,
                                           gettext('Interculturalidad'),
                                           gettext("Entre ") + studentName[2] + " " + studentName[3] + gettext(
                                               " y ") + otherStudents,
                                           URL, etapa,
                                           gettext(
                                               'El número de compañeros por los que se cree rechazado o percepción negativa (PN) es alta y su percepción acertada de ese número (PAN) es alta.'),
                                           reasons,
                                           'Educación en valores', 'Interculturalidad', gettext(
                                'Cuando un alumno tenga un índice de percepción negativa alto y un índice de acierto alto y se dé la circunstancia de la multiculturalidad (raza, etnia, religión, etc.).'))

                        getRecommendations(recommendations, 'PN', 2, gettext('Educación en valores'), 2,
                                           gettext('Respeto y tolerancia'),
                                           gettext("Entre ") + studentName[2] + " " + studentName[3] + gettext(
                                               " y ") + otherStudents,
                                           URL, etapa,
                                           gettext(
                                               'El número de compañeros por los que se cree rechazado o percepción negativa (PN) es alta y su percepción acertada de ese número (PAN) es alta y se dan las circunstancias de diversidad funcional o singularidad física o psíquica, identidad de género, diferencias socioeconómicas, etc.'),
                                           reasons,
                                           'Educación en valores', 'Respeto y tolerancia')

                        getRecommendations(recommendations, 'PN', 2, gettext('Educación en valores'), 4,
                                           gettext('Responsabilidad'),
                                           gettext("Entre ") + studentName[2] + " " + studentName[3] + gettext(
                                               " y ") + otherStudents,
                                           URL, etapa,
                                           gettext(
                                               'El número de compañeros por los que se cree rechazado o percepción negativa (PN) es alta y su percepción acertada de ese número (PAN) es alta en preguntas de ámbtio formal.'),
                                           reasons,
                                           'Educación en valores', 'Responsabilidad')

            otherStudents = ''
            reasons = ''
            if ipnValue[user][list(ipnValue[user])[0]] == gettext("Alto"):
                for r in matrix[6][user]:
                    o = db.session.query(Alumno, AlumnosTest.c.code, User.nombre, User.apellidos).join(AlumnosTest,
                                                                                                       and_(
                                                                                                           AlumnosTest.c.code == r,
                                                                                                           AlumnosTest.c.alumno == Alumno.id, )) \
                        .join(User, User.id == Alumno.user).one()
                    if list(matrix[6][user][r].values())[0] != '':
                        if otherStudents == '':
                            otherStudents += o[2] + " " + o[3]
                        else:
                            otherStudents += "/" + o[2] + " " + o[3]
                    if alumnoCurrent != '':
                        if r in matrixText[6][user]:
                            if matrixText[6][user][r] != '':
                                reasons += o[2] + " " + o[3] + gettext(
                                    ' lo/la eligió por el motivo "') + matrixText[6][user][r] + '". '
                            else:
                                reasons += o[2] + " " + o[3] + gettext(' lo/la eligió') + '. '

                if otherStudents != '':

                    getRecommendations(recommendations, 'IPN', 2, gettext('Educación en valores'), 2,
                                       gettext('Respeto y tolerancia'),
                                       gettext("Entre ") + studentName[2] + " " + studentName[3] + gettext(
                                           " y ") + otherStudents,
                                       URL, etapa,
                                       gettext(
                                           'La cantidad de veces que es nombrado/a por sus compañeros en las categorías de carácter negativo o el índice de preferencia social negativa (IPN) es alto.'),
                                       reasons,
                                       'Educación en valores', 'Respeto y tolerancia', gettext('Cuando el índice afecta al atributo de "no respeta" o similar.'))

                    getRecommendations(recommendations, 'IPN', 2, gettext('Educación en valores'), 4,
                                       gettext('Responsabilidad'),
                                       gettext("Entre ") + studentName[2] + " " + studentName[3] + gettext(
                                           " y ") + otherStudents,
                                       URL, etapa,
                                       gettext(
                                           'La cantidad de veces que es nombrado/a por sus compañeros en las categorías de carácter negativo o el índice de preferencia social negativa (IPN) es alto.'),
                                       reasons,
                                       'Educación en valores', 'Responsabilidad', gettext('Cuando el índice afecta al atributo de "no trabaja" o "no colabora" o similar.'))


        return {'ic': icValue, 'id': idValue,
                'iap': iapValue, 'ian': ianValue, 'recomendaciones': recommendations, 'sp': spValue, 'sn': snValue,
                'ep': epValue, 'en': enValue, 'pp': ppValue, 'pap': papValue, 'pn': pnValue, 'pan': panValue,
                'ip': ipValue, 'in': inValue, 'ipp': ippValue, 'ipn': ipnValue, 'imp': impValue, 'imn': imnValue}
    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)


def processAnswersMatrix(body, matrix, matrix12, matrix34, sp, spval, sn, snval, ip, ipval, iN, inval, ipp, ipval5, ipn,
                         inval6, respuestasNum, complete):
    try:
        mutual, os, reject, believe, believeNo, oip, oin = 0, 0, 0, 0, 0, 0, 0
        for pregunta in matrix:  # itera las 6 preguntas
            for answer in matrix[pregunta]:  # itera las respuestas de cada alumno a una pregunta
                if complete:
                    answerId = db.session.query(Alumno, AlumnosTest.c.code).join(AlumnosTest,
                                                                                 and_(
                                                                                     AlumnosTest.c.code == answer,
                                                                                     AlumnosTest.c.alumno == Alumno.id, )).one()
                # INICIALIZAR VARIABLES
                if str(answer) not in matrix12:
                    matrix12[str(answer)] = {}
                if 'EP' not in matrix12[str(answer)]:
                    matrix12[str(answer)]['EP'] = 0
                if 'EN' not in matrix12[str(answer)]:
                    matrix12[str(answer)]['EN'] = 0
                if 'RP' not in matrix12[str(answer)]:
                    matrix12[str(answer)]['RP'] = 0
                if 'RN' not in matrix12[str(answer)]:
                    matrix12[str(answer)]['RN'] = 0

                if str(answer) not in matrix34:
                    matrix34[str(answer)] = {}
                if 'PP' not in matrix34[str(answer)]:
                    matrix34[str(answer)]['PP'] = 0
                if 'PN' not in matrix34[str(answer)]:
                    matrix34[str(answer)]['PN'] = 0
                if 'PAP' not in matrix34[str(answer)]:
                    matrix34[str(answer)]['PAP'] = 0
                if 'PAN' not in matrix34[str(answer)]:
                    matrix34[str(answer)]['PAN'] = 0
                # FIN INICIALIZAR VARIABLES

                # ITERAR LA PUNTUACION DADA A CADA ESTUDIANTES POR UN ALUMNO EN UNA PREGUNTA
                for student in matrix[pregunta][answer]:

                    # INICIALIZAR VARIABLES
                    if student not in sp:
                        sp[student] = 0
                    if student not in spval:
                        spval[student] = 0

                    if student not in sn:
                        sn[student] = 0
                    if student not in snval:
                        snval[student] = 0

                    if student not in ip:
                        ip[student] = 0
                    if student not in ipval:
                        ipval[student] = 0

                    if student not in iN:
                        iN[student] = 0
                    if student not in inval:
                        inval[student] = 0

                    if student not in ipp:
                        ipp[student] = 0
                    if student not in ipval5:
                        ipval5[student] = 0

                    if student not in ipn:
                        ipn[student] = 0
                    if student not in inval6:
                        inval6[student] = 0
                    # FIN INICIALIZAR VARIABLES

                    if not complete:
                        empty = {str('#000000'): str('')}
                    else:
                        empty = ''
                    # CASO EN EL QUE student HAYA SIDO SELECCIONADO COMO RESPUESTA PARA LA PREGUNTA
                    if matrix[pregunta][answer][student] != empty:

                        if pregunta == 1:  # TIPO PGP

                            # CALCULOS ECUACIONES VARIABLES
                            matrix12[str(answer)]['EP'] += 1
                            sp[student] += 1
                            if not complete:
                                spval[student] += int(
                                    matrix[pregunta][answer][student][list(matrix[pregunta][answer][student])[0]])
                            else:
                                spval[student] += int(matrix[pregunta][answer][student])
                            # FIN CALCULOS ECUACIONES VARIABLES

                            if student in matrix[pregunta]:
                                if matrix[pregunta][student][answer] != empty:
                                    matrix12[str(answer)]['RP'] += 1
                                    if not complete:

                                        if '#000000' in matrix[pregunta][answer][student]:
                                            matrix[pregunta][answer][student]['#d6c22b'] = \
                                                matrix[pregunta][answer][student][
                                                    '#000000']
                                            del matrix[pregunta][answer][student]['#000000']
                                        if '#000000' in matrix[pregunta][student][answer]:
                                            matrix[pregunta][student][answer][str('#d6c22b')] = \
                                                matrix[pregunta][student][answer][
                                                    '#000000']
                                            del matrix[pregunta][student][answer]['#000000']
                                    else:
                                        mutual += 1
                                        studentId = db.session.query(Alumno, AlumnosTest.c.code).join(AlumnosTest,
                                                                                                      and_(
                                                                                                          AlumnosTest.c.code == student,
                                                                                                          AlumnosTest.c.alumno == Alumno.id, )).one()
                                        if '#ffffff' in \
                                                respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][answerId[1]][
                                                    str(student)]:
                                            respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][answerId[1]][
                                                str(student)][
                                                str('#d6c22b')] = \
                                                respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][answerId[1]][
                                                    str(student)][
                                                    '#ffffff']
                                            del \
                                                respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][answerId[1]][
                                                    str(student)][
                                                    '#ffffff']
                                        if '#ffffff' in \
                                                respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][studentId[1]][
                                                    str(answer)]:
                                            respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][studentId[1]][
                                                str(answer)][
                                                str('#d6c22b')] = \
                                                respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][studentId[1]][
                                                    str(answer)][
                                                    '#ffffff']
                                            del \
                                                respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][studentId[1]][
                                                    str(answer)][
                                                    '#ffffff']
                                if matrix[pregunta + 1][student][answer] != empty:
                                    if not complete:
                                        if '#000000' in matrix[pregunta][answer][student]:
                                            matrix[pregunta][answer][student][str('#e05ab8')] = \
                                                matrix[pregunta][answer][student][
                                                    '#000000']
                                            del matrix[pregunta][answer][student]['#000000']
                                        if '#000000' in matrix[pregunta + 1][student][answer]:
                                            matrix[pregunta + 1][student][answer][str('#e05ab8')] = \
                                                matrix[pregunta + 1][student][answer]['#000000']
                                            del matrix[pregunta + 1][student][answer]['#000000']
                                    else:
                                        os += 1
                                        studentId = db.session.query(Alumno, AlumnosTest.c.code).join(AlumnosTest,
                                                                                                      and_(
                                                                                                          AlumnosTest.c.code == student,
                                                                                                          AlumnosTest.c.alumno == Alumno.id, )).one()
                                        if '#ffffff' in \
                                                respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][answerId[1]][
                                                    str(student)]:
                                            respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][answerId[1]][
                                                str(student)][
                                                str('#e05ab8')] = \
                                                respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][answerId[1]][
                                                    str(student)][
                                                    '#ffffff']
                                            del \
                                                respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][answerId[1]][
                                                    str(student)][
                                                    '#ffffff']
                                        if '#ffffff' in \
                                                respuestasNum[pregunta + 1][list(respuestasNum[pregunta + 1])[0]][
                                                    studentId[1]][
                                                    str(answer)]:
                                            respuestasNum[pregunta + 1][list(respuestasNum[pregunta + 1])[0]][
                                                studentId[1]][
                                                str(answer)][str('#e05ab8')] = \
                                                respuestasNum[pregunta + 1][list(respuestasNum[pregunta + 1])[0]][
                                                    studentId[1]][
                                                    str(answer)]['#ffffff']
                                            del respuestasNum[pregunta + 1][list(respuestasNum[pregunta + 1])[0]][
                                                studentId[1]][
                                                str(answer)]['#ffffff']
                        elif pregunta == 2:
                            matrix12[str(answer)]['EN'] += 1
                            sn[student] += 1
                            if not complete:
                                snval[student] += int(
                                    matrix[pregunta][answer][student][list(matrix[pregunta][answer][student])[0]])
                            else:
                                int(matrix[pregunta][answer][student])
                            if student in matrix[pregunta]:
                                if matrix[pregunta][student][answer] != empty:
                                    matrix12[str(answer)]['RN'] += 1
                                    if not complete:
                                        if '#000000' in matrix[pregunta][answer][student]:
                                            matrix[pregunta][answer][student][str('#0da863')] = \
                                                matrix[pregunta][answer][student][
                                                    '#000000']
                                            del matrix[pregunta][answer][student]['#000000']
                                        if '#000000' in matrix[pregunta][student][answer]:
                                            matrix[pregunta][student][answer][str('#0da863')] = \
                                                matrix[pregunta][student][answer][
                                                    '#000000']
                                            del matrix[pregunta][student][answer]['#000000']
                                    else:
                                        reject += 1
                                        studentId = db.session.query(Alumno, AlumnosTest.c.code).join(AlumnosTest,
                                                                                                      and_(
                                                                                                          AlumnosTest.c.code == student,
                                                                                                          AlumnosTest.c.alumno == Alumno.id, )).one()
                                        if '#ffffff' in \
                                                respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][answerId[1]][
                                                    str(student)]:
                                            respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][answerId[1]][
                                                str(student)][
                                                str('#0da863')] = \
                                                respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][answerId[1]][
                                                    str(student)][
                                                    '#ffffff']
                                            del \
                                                respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][answerId[1]][
                                                    str(student)][
                                                    '#ffffff']
                                        if '#ffffff' in \
                                                respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][studentId[1]][
                                                    str(answer)]:
                                            respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][studentId[1]][
                                                str(answer)][
                                                str('#0da863')] = \
                                                respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][studentId[1]][
                                                    str(answer)][
                                                    '#ffffff']
                                            del \
                                                respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][studentId[1]][
                                                    str(answer)][
                                                    '#ffffff']
                        elif pregunta == 3:
                            ip[student] += 1
                            matrix34[str(answer)]['PP'] += 1
                            if not complete:
                                ipval[student] += int(
                                    matrix[pregunta][answer][student][list(matrix[pregunta][answer][student])[0]])
                            else:
                                ipval[student] += int(matrix[pregunta][answer][student])
                            if student in matrix[pregunta]:
                                if matrix[pregunta - 2][student][answer] != empty:
                                    matrix34[str(answer)]['PAP'] += 1
                                    if not complete:
                                        if '#000000' in matrix[pregunta][answer][student]:
                                            matrix[pregunta][answer][student][str('#349beb')] = \
                                                matrix[pregunta][answer][student][
                                                    '#000000']
                                            del matrix[pregunta][answer][student]['#000000']
                                    else:
                                        believe += 1
                                        if '#ffffff' in \
                                                respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][answerId[1]][
                                                    str(student)]:
                                            respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][answerId[1]][
                                                str(student)][
                                                str('#349beb')] = \
                                                respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][answerId[1]][
                                                    str(student)][
                                                    '#ffffff']
                                            del \
                                                respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][answerId[1]][
                                                    str(student)][
                                                    '#ffffff']
                                elif matrix[pregunta - 1][student][answer] != empty:
                                    if not complete:
                                        if '#000000' in matrix[pregunta][answer][student]:
                                            matrix[pregunta][answer][student][str('#ed3e46')] = \
                                                matrix[pregunta][answer][student][
                                                    '#000000']
                                            del matrix[pregunta][answer][student]['#000000']
                                    else:
                                        oip += 1
                                        if '#ffffff' in \
                                                respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][answerId[1]][
                                                    str(student)]:
                                            respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][answerId[1]][
                                                str(student)][
                                                str('#ed3e46')] = \
                                                respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][answerId[1]][
                                                    str(student)][
                                                    '#ffffff']
                                            del \
                                                respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][answerId[1]][
                                                    str(student)][
                                                    '#ffffff']
                        elif pregunta == 4:
                            iN[student] += 1
                            matrix34[str(answer)]['PN'] += 1
                            if not complete:
                                inval[student] += int(
                                    matrix[pregunta][answer][student][list(matrix[pregunta][answer][student])[0]])
                            else:
                                inval[student] += int(matrix[pregunta][answer][student])
                            if student in matrix[pregunta]:
                                if matrix[pregunta - 2][student][answer] != empty:
                                    matrix34[str(answer)]['PAN'] += 1
                                    if not complete:
                                        if '#000000' in matrix[pregunta][answer][student]:
                                            matrix[pregunta][answer][student][str('#eb8034')] = \
                                                matrix[pregunta][answer][student][
                                                    '#000000']
                                            del matrix[pregunta][answer][student]['#000000']
                                    else:
                                        believeNo += 1
                                        if '#ffffff' in \
                                                respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][answerId[1]][
                                                    str(student)]:
                                            respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][answerId[1]][
                                                str(student)][
                                                str('#eb8034')] = \
                                                respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][answerId[1]][
                                                    str(student)][
                                                    '#ffffff']
                                            del \
                                                respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][answerId[1]][
                                                    str(student)][
                                                    '#ffffff']
                                elif matrix[pregunta - 3][student][answer] != empty:
                                    if not complete:
                                        if '#000000' in matrix[pregunta][answer][student]:
                                            matrix[pregunta][answer][student][str('#9646e0')] = \
                                                matrix[pregunta][answer][student][
                                                    '#000000']
                                            del matrix[pregunta][answer][student]['#000000']
                                    else:
                                        oin += 1
                                        if '#ffffff' in \
                                                respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][answerId[1]][
                                                    str(student)]:
                                            respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][answerId[1]][
                                                str(student)][
                                                str('#9646e0')] = \
                                                respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][answerId[1]][
                                                    str(student)][
                                                    '#ffffff']
                                            del \
                                                respuestasNum[pregunta][list(respuestasNum[pregunta])[0]][answerId[1]][
                                                    str(student)][
                                                    '#ffffff']
                        elif pregunta == 5:
                            if not complete:
                                ipval5[student] += int(
                                    matrix[pregunta][answer][student][list(matrix[pregunta][answer][student])[0]])
                            else:
                                ipval5[student] += int(matrix[pregunta][answer][student])
                        elif pregunta == 6:
                            if not complete:
                                inval6[student] += int(
                                    matrix[pregunta][answer][student][list(matrix[pregunta][answer][student])[0]])
                            else:
                                inval6[student] += int(matrix[pregunta][answer][student])
        if complete:
            return mutual, os, reject, believe, believeNo, oip, oin
        else:
            return
    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)


def calculateDataSP(data1, data2, sp, num_alumnos, sn):
    try:
        data1[1] = {'d': float(sum(sp.values())) / num_alumnos}
        data1[2] = {'p': float(data1[1]['d']) / (num_alumnos - 1)}
        data1[3] = {'qq': 1 - data1[2]['p']}
        data1[4] = {'M': data1[2]['p'] * (num_alumnos - 1)}
        data1[5] = {'ss': math.sqrt((num_alumnos - 1) * data1[2]['p'] * data1[3]['qq'])}
        if data1[5]['ss'] != 0:
            data1[6] = {'a': (data1[3]['qq'] - data1[2]['p']) / data1[5]['ss']}
        else:
            data1[6] = {'a': 0}
        data1[7] = {'Xsup': data1[4]['M'] + get_t(data1[6]['a'], False) * data1[5]['ss']}
        data1[8] = {'Xinf': data1[4]['M'] + get_t(data1[6]['a'], True) * data1[5]['ss']}

        data2[1] = {'d': float(sum(sn.values())) / num_alumnos}
        data2[2] = {'p': float(data2[1]['d']) / (num_alumnos - 1)}
        data2[3] = {'qq': 1 - data2[2]['p']}
        data2[4] = {'M': data2[2]['p'] * (num_alumnos - 1)}
        data2[5] = {'ss': math.sqrt((num_alumnos - 1) * data2[2]['p'] * data2[3]['qq'])}
        if data2[5]['ss'] != 0:
            data2[6] = {'a': (data2[3]['qq'] - data2[2]['p']) / data2[5]['ss']}
        else:
            data2[6] = {'a': 0}
        data2[7] = {'Xsup': data2[4]['M'] + get_t(data2[6]['a'], False) * data2[5]['ss']}
        data2[8] = {'Xinf': data2[4]['M'] + get_t(data2[6]['a'], True) * data2[5]['ss']}
    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)


def calculateDataIP(data3, data4, ip, num_alumnos, iN):
    try:
        data3[1] = {'d': float(sum(ip.values())) / num_alumnos}
        data3[2] = {'p': float(data3[1]['d']) / (num_alumnos - 1)}
        data3[3] = {'qq': 1 - data3[2]['p']}
        data3[4] = {'M': data3[2]['p'] * (num_alumnos - 1)}
        data3[5] = {'ss': math.sqrt((num_alumnos - 1) * data3[2]['p'] * data3[3]['qq'])}
        if data3[5]['ss'] != 0:
            data3[6] = {'a': (data3[3]['qq'] - data3[2]['p']) / data3[5]['ss']}
        else:
            data3[6] = {'a': 0}
        data3[7] = {'Xsup': data3[4]['M'] + get_t(data3[6]['a'], False) * data3[5]['ss']}
        data3[8] = {'Xinf': data3[4]['M'] + get_t(data3[6]['a'], True) * data3[5]['ss']}

        data4[1] = {'d': float(sum(iN.values())) / num_alumnos}
        data4[2] = {'p': float(data4[1]['d']) / (num_alumnos - 1)}
        data4[3] = {'qq': 1 - data4[2]['p']}
        data4[4] = {'M': data4[2]['p'] * (num_alumnos - 1)}
        data4[5] = {'ss': math.sqrt((num_alumnos - 1) * data4[2]['p'] * data4[3]['qq'])}
        if data4[5]['ss'] != 0:
            data4[6] = {'a': (data4[3]['qq'] - data4[2]['p']) / data4[5]['ss']}
        else:
            data4[6] = {'a': 0}
        data4[7] = {'Xsup': data4[4]['M'] + get_t(data4[6]['a'], False) * data4[5]['ss']}
        data4[8] = {'Xinf': data4[4]['M'] + get_t(data4[6]['a'], True) * data4[5]['ss']}
    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)


def calculateNpNn(np, nn, spval, snval, num_alumnos):
    try:
        for s in spval:
            np[s] = int((float(spval[s]) / ((num_alumnos - 1) * 5)) * 100)
            nn[s] = int((float(snval[s]) / ((num_alumnos - 1) * 5)) * 100)
    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)


def calculateImpImnIppIpn(imp, imn, ipp, ipn, ipval, inval, ipval5, inval6, num_alumnos, ipp_bol, imp_bol):
    try:
        for s in ipval:
            if imp_bol:
                imp[s] = int((float(ipval[s]) / ((num_alumnos - 1) * 5)) * 100)
                imn[s] = int((float(inval[s]) / ((num_alumnos - 1) * 5)) * 100)
            if ipp_bol:
                ipp[s] = int((float(ipval5[s]) / ((num_alumnos - 1) * 5)) * 100)
                ipn[s] = int((float(inval6[s]) / ((num_alumnos - 1) * 5)) * 100)
    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)


def calculateGroupVariables(matrix12):
    try:
        ic, id = 0, 0
        for m in matrix12:
            for e in matrix12[m]:
                if e == "EP" or e == "EN":
                    matrix12[m][e] = int((float(matrix12[m][e]) / MAX_POINTS) * 100)
                elif e == "RP":
                    ic += matrix12[m][e]
                elif e == "RN":
                    id += matrix12[m][e]
        return ic, id
    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)


def calculatePapPanPpPn(matrix34, pp):
    try:
        for m in matrix34:
            for e in matrix34[m]:
                if e == "PAP":
                    if matrix34[m]['PP'] != 0:
                        matrix34[m][e] = int((float(matrix34[m][e]) / matrix34[m]['PP']) * 100)
                    else:
                        matrix34[m][e] = 0
                elif e == "PAN":
                    if matrix34[m]['PN'] != 0:
                        matrix34[m][e] = int((float(matrix34[m][e]) / matrix34[m]['PN']) * 100)
                    else:
                        matrix34[m][e] = 0
        if pp:
            for m in matrix34:
                for e in matrix34[m]:
                    if e == "PP" or e == "PN":
                        matrix34[m][e] = int((float(matrix34[m][e]) / MAX_POINTS) * 100)
    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)


def calculateRpRnOs(matrix, rp, rn, os, alumno, studentCurrent, index):
    try:
        for al in matrix[1]:
            if al == alumno:
                for st in matrix[1][al]:
                    if st in matrix[1]:
                        stOb = db.session.query(Alumno, AlumnosTest.c.code).join(Alumno,
                                                                                 and_(Alumno.id == AlumnosTest.c.alumno,
                                                                                      st == AlumnosTest.c.code)).one()
                        if "#d6c22b" in matrix[1][al][st] and "#d6c22b" in matrix[1][st][al]:
                            if (int(matrix[1][al][st]['#d6c22b']) == 5 or int(matrix[1][al][st]['#d6c22b']) == 4) and (
                                    int(matrix[1][st][al]['#d6c22b']) == 5 or int(matrix[1][st][al]['#d6c22b']) == 4):
                                rp[stOb[index]] = [gettext("FUERTE"), matrix[1][al][st]['#d6c22b'],
                                               matrix[1][st][al]['#d6c22b']]
                            elif int(matrix[1][al][st]['#d6c22b']) == 3 or int(matrix[1][st][al]['#d6c22b']) == 3 or (
                                    int(matrix[1][al][st]['#d6c22b']) == 2 and int(
                                matrix[1][st][al]['#d6c22b']) == 4) or (
                                    int(matrix[1][st][al]['#d6c22b']) == 2 and int(matrix[1][al][st]['#d6c22b']) == 4):
                                rp[stOb[index]] = [gettext("MEDIA"), matrix[1][al][st]['#d6c22b'],
                                               matrix[1][st][al]['#d6c22b']]
                            elif abs(int(matrix[1][al][st]['#d6c22b']) - int(matrix[1][st][al]['#d6c22b'])) >= 2:
                                rp[stOb[index]] = [gettext("DESIQUILIBRADA"), matrix[1][al][st]['#d6c22b'],
                                               matrix[1][st][al]['#d6c22b']]
                            else:
                                rp[stOb[index]] = [gettext("DÉBIL"), matrix[1][al][st]['#d6c22b'],
                                               matrix[1][st][al]['#d6c22b']]
                        elif "#e05ab8" in matrix[1][al][st] and "#e05ab8" in matrix[2][st][al]:
                            if (int(matrix[1][al][st]['#e05ab8']) == 5 or int(matrix[1][al][st]['#e05ab8']) == 4) and (
                                    int(matrix[2][st][al]['#e05ab8']) == 5 or int(matrix[2][st][al]['#e05ab8']) == 4):
                                os[stOb[index]] = [gettext("FUERTE"), matrix[1][al][st]['#e05ab8'],
                                               matrix[2][st][al]['#e05ab8'], studentCurrent, stOb[index]]
                            elif int(matrix[1][al][st]['#e05ab8']) == 3 or int(matrix[2][st][al]['#e05ab8']) == 3 or (
                                    int(matrix[1][al][st]['#e05ab8']) == 2 and int(
                                matrix[2][st][al]['#e05ab8']) == 4) or (
                                    int(matrix[2][st][al]['#e05ab8']) == 2 and int(matrix[1][al][st]['#e05ab8']) == 4):
                                os[stOb[index]] = [gettext("MEDIA"), matrix[1][al][st]['#e05ab8'],
                                               matrix[2][st][al]['#e05ab8'], studentCurrent, stOb[index]]
                            elif abs(int(matrix[1][al][st]['#e05ab8']) - int(matrix[2][st][al]['#e05ab8'])) >= 2:
                                os[stOb[index]] = [gettext("DESIQUILIBRADA"), matrix[1][al][st]['#e05ab8'],
                                               matrix[2][st][al]['#e05ab8'], studentCurrent, stOb[index]]
                            else:
                                os[stOb[index]] = [gettext("DÉBIL"), matrix[1][al][st]['#e05ab8'],
                                               matrix[2][st][al]['#e05ab8'], studentCurrent, stOb[index]]

        for al in matrix[2]:
            if al == alumno:
                for st in matrix[2][al]:
                    if st in matrix[2]:
                        stOb = db.session.query(Alumno, AlumnosTest.c.code).join(Alumno,
                                                                                 and_(Alumno.id == AlumnosTest.c.alumno,
                                                                                      st == AlumnosTest.c.code)).one()
                        if "#0da863" in matrix[2][al][st] and "#0da863" in matrix[2][st][al]:
                            if (int(matrix[2][al][st]['#0da863']) == 5 or int(matrix[2][al][st]['#0da863']) == 4) and (
                                    int(matrix[2][st][al]['#0da863']) == 5 or int(matrix[2][st][al]['#0da863']) == 4):
                                rn[stOb[index]] = [gettext("FUERTE"), matrix[2][al][st]['#0da863'],
                                               matrix[2][st][al]['#0da863']]
                            elif int(matrix[2][al][st]['#0da863']) == 3 or int(matrix[2][st][al]['#0da863']) == 3 or (
                                    int(matrix[2][al][st]['#0da863']) == 2 and int(
                                matrix[2][st][al]['#0da863']) == 4) or (
                                    int(matrix[2][st][al]['#0da863']) == 2 and int(matrix[2][al][st]['#0da863']) == 4):
                                rn[stOb[index]] = [gettext("MEDIA"), matrix[2][al][st]['#0da863'],
                                               matrix[2][st][al]['#0da863']]
                            elif abs(int(matrix[2][al][st]['#0da863']) - int(matrix[2][st][al]['#0da863'])) >= 2:
                                rn[stOb[index]] = [gettext("DESIQUILIBRADA"), matrix[2][al][st]['#0da863'],
                                               matrix[2][st][al]['#0da863']]
                            else:
                                rn[stOb[index]] = [gettext("DÉBIL"), matrix[2][al][st]['#0da863'],
                                               matrix[2][st][al]['#0da863']]
                        elif "#e05ab8" in matrix[2][al][st] and "#e05ab8" in matrix[1][st][al]:
                            if (int(matrix[2][al][st]['#e05ab8']) == 5 or int(matrix[2][al][st]['#e05ab8']) == 4) and (
                                    int(matrix[1][st][al]['#e05ab8']) == 5 or int(matrix[1][st][al]['#e05ab8']) == 4):
                                os[stOb[index]] = [gettext("FUERTE"), matrix[1][st][al]['#e05ab8'],
                                               matrix[2][al][st]['#e05ab8'], stOb[index], studentCurrent]
                            elif int(matrix[2][al][st]['#e05ab8']) == 3 or int(matrix[1][st][al]['#e05ab8']) == 3 or (
                                    int(matrix[2][al][st]['#e05ab8']) == 2 and int(
                                matrix[1][st][al]['#e05ab8']) == 4) or (
                                    int(matrix[1][st][al]['#e05ab8']) == 2 and int(matrix[2][al][st]['#e05ab8']) == 4):
                                os[stOb[index]] = [gettext("MEDIA"), matrix[1][st][al]['#e05ab8'],
                                               matrix[2][al][st]['#e05ab8'], stOb[index], studentCurrent]
                            elif abs(int(matrix[2][al][st]['#e05ab8']) - int(matrix[1][st][al]['#e05ab8'])) >= 2:
                                os[stOb[index]] = [gettext("DESIQUILIBRADA"), matrix[1][st][al]['#e05ab8'],
                                               matrix[2][al][st]['#e05ab8'], stOb[index], studentCurrent]
                            else:
                                os[stOb[index]] = [gettext("DÉBIL"), matrix[1][st][al]['#e05ab8'],
                                               matrix[2][al][st]['#e05ab8'], stOb[index], studentCurrent]
    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)


def calculateOipOin(matrix, oip, oin, alumno, index):
    try:
        for al in matrix[3]:
            if al == alumno:
                for st in matrix[3][al]:
                    if st in matrix[2]:
                        stOb = db.session.query(Alumno, AlumnosTest.c.code).join(Alumno,
                                                                                 and_(Alumno.id == AlumnosTest.c.alumno,
                                                                                      st == AlumnosTest.c.code)).one()
                        if "#ed3e46" in matrix[3][al][st] and "#ed3e46" in matrix[2][st][al]:
                            if (int(matrix[3][al][st]['#ed3e46']) == 5 or int(matrix[3][al][st]['#ed3e46']) == 4) and (
                                    int(matrix[2][st][al][list(matrix[2][st][al])[0]]) == 5 or int(
                                matrix[2][st][al][list(matrix[2][st][al])[0]]) == 4):
                                oip[stOb[index]] = [gettext("FUERTE"), matrix[3][al][st]['#ed3e46'],
                                                matrix[2][st][al][list(matrix[2][st][al])[0]]]
                            elif int(matrix[3][al][st]['#ed3e46']) == 3 or int(
                                    matrix[2][st][al][list(matrix[2][st][al])[0]]) == 3 or (
                                    int(matrix[3][al][st]['#ed3e46']) == 2 and int(
                                matrix[2][st][al][list(matrix[2][st][al])[0]]) == 4) or (
                                    int(matrix[2][st][al][list(matrix[2][st][al])[0]]) == 2 and int(
                                matrix[3][al][st]['#ed3e46']) == 4):
                                oip[stOb[index]] = [gettext("MEDIA"), matrix[3][al][st]['#ed3e46'],
                                                matrix[2][st][al][list(matrix[2][st][al])[0]]]
                            elif abs(int(matrix[3][al][st]['#ed3e46']) - int(
                                    matrix[2][st][al][list(matrix[2][st][al])[0]])) >= 2:
                                oip[stOb[index]] = [gettext("DESIQUILIBRADA"), matrix[3][al][st]['#ed3e46'],
                                                matrix[2][st][al][list(matrix[2][st][al])[0]]]
                            else:
                                oip[stOb[index]] = [gettext("DÉBIL"), matrix[3][al][st]['#ed3e46'],
                                                matrix[2][st][al][list(matrix[2][st][al])[0]]]

        for al in matrix[4]:
            if al == alumno:
                for st in matrix[4][al]:
                    if st in matrix[1]:
                        stOb = db.session.query(Alumno, AlumnosTest.c.code).join(Alumno,
                                                                                 and_(Alumno.id == AlumnosTest.c.alumno,
                                                                                      st == AlumnosTest.c.code)).one()
                        if "#9646e0" in matrix[4][al][st] and "#9646e0" in matrix[1][st][al]:
                            if (int(matrix[4][al][st]['#9646e0']) == 5 or int(matrix[4][al][st]['#9646e0']) == 4) and (
                                    int(matrix[1][st][al][list(matrix[1][st][al])[0]]) == 5 or int(
                                matrix[1][st][al][list(matrix[1][st][al])[0]]) == 4):
                                oin[stOb[index]] = [gettext("FUERTE"), matrix[1][st][al][list(matrix[1][st][al])[0]],
                                                matrix[4][al][st]['#9646e0']]
                            elif int(matrix[4][al][st]['#9646e0']) == 3 or int(
                                    matrix[1][st][al][list(matrix[1][st][al])[0]]) == 3 or (
                                    int(matrix[4][al][st]['#9646e0']) == 2 and int(
                                matrix[1][st][al][list(matrix[1][st][al])[0]]) == 4) or (
                                    int(matrix[1][st][al][list(matrix[1][st][al])[0]]) == 2 and int(
                                matrix[4][al][st]['#9646e0']) == 4):
                                oin[stOb[index]] = [gettext("MEDIA"), matrix[1][st][al][list(matrix[1][st][al])[0]],
                                                matrix[4][al][st]['#9646e0']]
                            elif abs(int(matrix[4][al][st]['#9646e0']) - int(
                                    matrix[1][st][al][list(matrix[1][st][al])[0]])) >= 2:
                                oin[stOb[index]] = [gettext("DESIQUILIBRADA"),
                                                matrix[1][st][al][list(matrix[1][st][al])[0]],
                                                matrix[4][al][st]['#9646e0']]
                            else:
                                oin[stOb[index]] = [gettext("DÉBIL"), matrix[1][st][al][list(matrix[1][st][al])[0]],
                                                matrix[4][al][st]['#9646e0']]
    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)


def return_tipo_pregunta(l, i):
    try:
        tipo_pregunta = TipoPregunta.query.get(l[i - 1].tipo_pregunta)
        return gettext(tipo_pregunta.descripcion)
    except:
        return None


def return_pregunta(l, i):
    try:
        return gettext(l[i - 1].pregunta.strip())
    except:
        return None


def return_value(l, value):
    for al in l:
        for color in l[al]:
            if l[al][color] != '':
                if int(l[al][color]) == value:
                    alumno = db.session.query(Alumno, User).join(AlumnosTest,
                                                                 and_(
                                                                     al == AlumnosTest.c.code,
                                                                     AlumnosTest.c.alumno == Alumno.id, )) \
                        .join(User, User.id == Alumno.user).one()
                    return alumno[1].nombre + " " + alumno[1].apellidos
    return ''


def return_text(l, value):
    for al in l:
        for color in l[al]:
            if l[al][color] != '':
                if int(l[al][color]) == value:
                    return al
    return ''

def return_link(l):
    try:
        for ans in l:
            return l[ans][0]

        return None
    except:
        return None

def return_des(l):
    try:
        for num in l:
            for ex in l[num]:
                for innum in l[num][ex]:
                    for inname in l[num][ex][innum]:
                        for ans in l[num][ex][innum][inname]:
                            return l[num][ex][innum][inname][ans][1]

        return None
    except:
        return None


def not_empty(l):
    try:
        for num in l:
            for ex in l[num]:
                for innum in l[num][ex]:
                    for inname in l[num][ex][innum]:
                        for ans in l[num][ex][innum][inname]:
                            return True
        return False
    except:
        return None


def not_empty_ex(l):
    try:
        for innum in l:
            for inname in l[innum]:
                for ans in l[innum][inname]:
                    return True
        return False
    except:
        return None


def addLinePdf(data, value, title):
    try:
        aux = []
        aux.append(title)
        if value:
            aux.append(value)
        else:
            aux.append('')
        data.append(aux)
    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)


def addTablePdf(proposals, elements, data, style, sLeft, alumno, bold, boldPreguntas, pos, ap1, ap2, ap3, ap4, ap7, ap8,
                ap11,
                ap12, ap15, ap16, ap17, ap18, italic, matrices, data_matrix, spaceAfter, spaceBefore, colWidths):
    try:
        dataAux = []
        for r, row in enumerate(data):
            aux = []
            for c, cell in enumerate(row):
                sLeft.textColor = 'black'
                if ((r == 0 and bold) or pos) or (
                        (((0 <= c <= len(row) - 1) and r == 0) or r == 2) and boldPreguntas) or (
                        (0 <= c <= len(row) - 1) and r == 0 and matrices):
                    sLeft.fontName = 'Helvetica-Bold'
                    sLeft.textColor = 'black'
                elif (c == 0 and (0 <= r <= len(data) - 1)) and italic:
                    sLeft.fontName = 'Helvetica-Oblique'
                    sLeft.textColor = 'black'
                else:
                    sLeft.fontName = 'Helvetica'
                    if ap1 or ap2 or ap3 or ap7 or ap8 or ap11 or ap12 or ap15 or ap16 or ap17 or ap18:
                        if c == 0 and (ap1 or ap2 or ap3 or ap15 or ap16):
                            if proposals['sp'][alumno][list(proposals['sp'][alumno])[0]] == gettext(
                                    "Bajo") and (ap1 or ap2):
                                sLeft.textColor = 'red'
                            elif proposals['sn'][alumno][list(proposals['sn'][alumno])[0]] == gettext(
                                    "Alto") and ap3:
                                sLeft.textColor = 'red'
                            elif proposals['ip'][alumno][list(proposals['ip'][alumno])[0]] == gettext("Bajo") and ap15:
                                sLeft.textColor = 'red'
                            elif proposals['in'][alumno][list(proposals['in'][alumno])[0]] == gettext("Alto") and ap16:
                                sLeft.textColor = 'red'
                            else:
                                sLeft.textColor = 'black'
                        elif c == 1 and not ap2:
                            if proposals['sn'][alumno][list(proposals['sn'][alumno])[0]] == gettext(
                                    "Alto") and (ap1 or ap3):
                                sLeft.textColor = 'red'
                            elif proposals['ep'][alumno][list(proposals['ep'][alumno])[0]] == gettext(
                                    "Bajo") and ap7:
                                sLeft.textColor = 'red'
                            elif proposals['pp'][alumno][list(proposals['pp'][alumno])[0]] == gettext(
                                    "Bajo") and ap8:
                                sLeft.textColor = 'red'
                            elif proposals['en'][alumno][list(proposals['en'][alumno])[0]] == gettext("Alto") and ap11:
                                sLeft.textColor = 'red'
                            elif proposals['pn'][alumno][list(proposals['pn'][alumno])[0]] == gettext("Alto") and ap12:
                                sLeft.textColor = 'red'
                            elif proposals['ip'][alumno][list(proposals['ip'][alumno])[0]] == gettext("Bajo") and ap15:
                                sLeft.textColor = 'red'
                            elif proposals['in'][alumno][list(proposals['in'][alumno])[0]] == gettext("Alto") and ap16:
                                sLeft.textColor = 'red'
                            elif proposals['ipp'][alumno][list(proposals['ipp'][alumno])[0]] == gettext(
                                    "Alto") and ap17:
                                sLeft.textColor = 'red'
                            elif proposals['ipn'][alumno][list(proposals['ipn'][alumno])[0]] == gettext(
                                    "Alto") and ap18:
                                sLeft.textColor = 'red'
                            else:
                                sLeft.textColor = 'black'
                        elif c == 2 and ap1:
                            percent = int(cell[0:-1])
                            if percent <= 25:
                                sLeft.textColor = 'red'
                            else:
                                sLeft.textColor = 'black'
                        elif c == 3 and (ap15 or ap16):
                            if proposals['imp'][alumno][list(proposals['imp'][alumno])[0]] == gettext("Alto") and ap15:
                                sLeft.textColor = 'red'
                            elif proposals['imn'][alumno][list(proposals['imn'][alumno])[0]] == gettext(
                                    "Alto") and ap16:
                                sLeft.textColor = 'red'
                            else:
                                sLeft.textColor = 'black'
                        else:
                            percent = int(cell[0:-1])
                            if ap1 or ap3 or ap11 or ap12 or ap15 or ap16 or ap17 or ap18:
                                if percent >= 75:
                                    sLeft.textColor = 'red'
                                else:
                                    sLeft.textColor = 'black'
                            elif ap2 or ap7 or ap8:
                                if percent <= 25:
                                    sLeft.textColor = 'red'
                                else:
                                    sLeft.textColor = 'black'
                    elif cell == str(gettext("No hay")) and ap4:
                        sLeft.textColor = 'red'
                    elif matrices:
                        if data_matrix:
                            if 'group' in data_matrix:
                                if r == 1 and data_matrix['group'] == 1:
                                    percent = int(cell)
                                    if percent < data_matrix[8]['Xinf']:
                                        sLeft.textColor = 'red'
                                    else:
                                        sLeft.textColor = 'black'
                                elif r == 1 and data_matrix['group'] < 5:
                                    percent = int(cell)
                                    if percent >= data_matrix[7]['Xsup']:
                                        sLeft.textColor = 'red'
                                    else:
                                        sLeft.textColor = 'black'
                                elif r == 1 and data_matrix['group'] >= 5:
                                    percent = int(cell[0:-1])
                                    if percent >= 75:
                                        sLeft.textColor = 'red'
                                    else:
                                        sLeft.textColor = 'black'
                                elif r == 3:
                                    percent = int(cell[0:-1])
                                    if (percent <= 25 and data_matrix['group'] == 1) or (
                                            percent >= 75 and data_matrix['group'] in (2, 3, 4)):
                                        sLeft.textColor = 'red'
                                    else:
                                        sLeft.textColor = 'black'
                                else:
                                    sLeft.textColor = 'black'
                            else:
                                if c == 0:
                                    if data_matrix['c'][0] in cell or data_matrix['c'][1] in cell:
                                        sLeft.textColor = 'red'
                                    else:
                                        sLeft.textColor = 'black'
                                else:
                                    if data_matrix['c'][1] in cell:
                                        sLeft.textColor = 'red'
                                    else:
                                        sLeft.textColor = 'black'
                        else:
                            if c == 1:
                                percent = int(cell[0:-1])
                                if percent <= 25:
                                    sLeft.textColor = 'red'
                                else:
                                    sLeft.textColor = 'black'
                            elif c == 3:
                                percent = int(cell[0:-1])
                                if percent >= 75:
                                    sLeft.textColor = 'red'
                                else:
                                    sLeft.textColor = 'black'
                            else:
                                sLeft.textColor = 'black'
                sLeft.fontSize = 9
                aux.append(Paragraph(str(cell), sLeft))
            dataAux.append(aux)
        if colWidths:
            t = Table(dataAux, spaceAfter=spaceAfter, spaceBefore=spaceBefore, colWidths=colWidths)
        else:
            t = Table(dataAux, spaceAfter=spaceAfter, spaceBefore=spaceBefore)
        t.setStyle(TableStyle(style))

        elements.append(t)
    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)


def producePdf(alumno, studentCurrent, test, matrix, preguntas, teacherProfile, clase, matrixText, sp, sn, matrix12,
               matrix34,
               proposals, position, np, nn, rp, rn, os, oip, oin, ip, iN, ipp, ipn, imp, imn, body, all):
    try:
        # INICIALIZAR PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=100, bottomMargin=50)
        doc.pagesize = portrait(A4)
        elements = []

        # CONFIGURAR ESTILO ALINEACION CENTRADA
        s = getSampleStyleSheet()
        s = s['BodyText']
        s.wordWrap = 'CJK'
        s.fontName = 'Helvetica'
        s.alignment = 1

        # FONT SIZE TITULO
        s.fontSize = 20
        # TITULO
        title = Paragraph(
            gettext("Informe de {0} {1}".format(studentCurrent[2].nombre, studentCurrent[2].apellidos)), s)
        elements.append(title)

        # FONT SIZE TEXTO
        s.fontSize = 10

        # CONFIGURAR ESTILO ALINEACION IZQUIERDA
        sLeft = getSampleStyleSheet()
        sLeft = sLeft['BodyText']
        sLeft.wordWrap = 'CJK'
        sLeft.fontName = 'Helvetica'
        sLeft.alignment = 0
        sLeft.fontSize = 10

        data = []
        aux = []

        # DATOS ALUMNO ACTUAL
        # ALIAS
        addLinePdf(data, studentCurrent[3], gettext("Alias"))
        # DNI
        addLinePdf(data, studentCurrent[2].DNI, gettext("DNI"))
        # FECHA DE NACIMIENTO
        addLinePdf(data, studentCurrent[2].fecha_nacimiento, gettext("Fecha de nacimiento"))
        # SEXO
        addLinePdf(data, studentCurrent[0].sexo_display, gettext("Sexo"))
        # CLASE
        addLinePdf(data, clase.nombre, gettext("Clase"))
        # TUTOR
        addLinePdf(data, teacherProfile[1].nombre + " " + teacherProfile[1].apellidos,
                   gettext(gettext("Tutor responsable")))
        # NOMBRE TEST
        addLinePdf(data, test.nombre, gettext("Nombre del test"))
        # FECHA
        addLinePdf(data, str(test.date_created.strftime('%d/%m/%Y %H:%M')), gettext("Fecha de creación del test"))

        # ADD TABLE
        addTablePdf(proposals, elements, data, style1, sLeft, alumno, bold=False, boldPreguntas=False, pos=False,
                    ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False, ap12=False,
                    ap15=False, ap16=False, ap17=False, ap18=False, italic=True, matrices=False, data_matrix={},
                    spaceAfter=50, spaceBefore=50, colWidths=())

        # ADD TITUTLO RESULTADOS
        s.fontName = 'Helvetica-Bold'
        s.fontSize = 14
        elements.append(Paragraph(gettext("Resultados de las preguntas"), s))

        # ADD ESPACIO
        s.fontName = 'Helvetica'
        elements.append(Spacer(1, 0.25 * inch))

        # ADD PREGUNTAS Y RESPUESTAS DEL ALUMNO
        for num in matrix:
            data = []
            aux = []
            s.fontSize = 12
            elements.append(Paragraph(
                gettext("Pregunta") + " #" + str(num) + ".- " + return_tipo_pregunta(preguntas, num) + " (" + gettext(
                    "Tipo") + " " + str(num) + ") ", s))
            s.fontSize = 9
            elements.append(Spacer(1, 0.15 * inch))
            elements.append(Paragraph(return_pregunta(preguntas, num), s))
            aux.append("1º")
            aux.append("2º")
            aux.append("3º")
            aux.append("4º")
            aux.append("5º")
            data.append(aux)
            aux = []
            for user in matrix[num]:
                if user == studentCurrent[1]:
                    # ORDEN DE LOS ALUMNOS SELECCIONADOS EN LAS RESPUESTAS
                    aux.append(return_value(matrix[num][user], 5))
                    aux.append(return_value(matrix[num][user], 4))
                    aux.append(return_value(matrix[num][user], 3))
                    aux.append(return_value(matrix[num][user], 2))
                    aux.append(return_value(matrix[num][user], 1))
                    data.append(aux)
                    aux = []
                    if num == 2 or num == 4 or num == 6:  # PREGUNTAS NEGATIVAS
                        aux.append(gettext('¿Por qué?'))
                        data.append(aux)
                        aux = []
                        # RESPUESTA EN TEXTO POR ORDEN DE SELECCION
                        for userText in matrixText[num][studentCurrent[1]]:
                            if userText == return_text(matrix[num][user], 5):
                                aux.append(matrixText[num][studentCurrent[1]][userText])
                        for userText in matrixText[num][studentCurrent[1]]:
                            if userText == return_text(matrix[num][user], 4):
                                aux.append(matrixText[num][studentCurrent[1]][userText])
                        for userText in matrixText[num][studentCurrent[1]]:
                            if userText == return_text(matrix[num][user], 3):
                                aux.append(matrixText[num][studentCurrent[1]][userText])
                        for userText in matrixText[num][studentCurrent[1]]:
                            if userText == return_text(matrix[num][user], 2):
                                aux.append(matrixText[num][studentCurrent[1]][userText])
                        for userText in matrixText[num][studentCurrent[1]]:
                            if userText == return_text(matrix[num][user], 1):
                                aux.append(matrixText[num][studentCurrent[1]][userText])
                        data.append(aux)
                        aux = []

            # ADD TABLE
            addTablePdf(proposals, elements, data, style1, sLeft, alumno, bold=False, boldPreguntas=True, pos=False,
                        ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False, ap12=False,
                        ap15=False, ap16=False, ap17=False, ap18=False, italic=False, matrices=False, data_matrix={},
                        spaceAfter=50, spaceBefore=20, colWidths=())

        # CAMBIO DE PAGINA
        elements.append(PageBreak())
        doc.pagesize = landscape(A4)

        # ADD TITULO ANALISIS
        s.fontName = 'Helvetica-Bold'
        s.fontSize = 14
        elements.append(Paragraph(gettext("Análisis de resultados"), s))

        # ADD ESPACIO
        s.fontName = 'Helvetica'
        elements.append(Spacer(1, 0.25 * inch))

        # ADD APARTADO 1 POSICION SOCIOMETRICA SP, SN, EP Y EN
        if body['sp'] or body['ep']:
            s.fontSize = 12
            if body['sp'] and body['ep']:
                elements.append(Paragraph(gettext("1.- POSICIÓN SOCIOMÉTRICA (SP, SN, EP Y EN)"), s))
            elif body['sp']:
                elements.append(Paragraph(gettext("1.- POSICIÓN SOCIOMÉTRICA (SP Y SN)"), s))
            else:
                elements.append(Paragraph(gettext("1.- POSICIÓN SOCIOMÉTRICA (EP Y EN)"), s))

            # ADD VALORES TABLA
            s.fontSize = 9
            data = []
            aux = []
            if body['sp']:
                aux.append("SP")
                aux.append("SN")
            if body['ep']:
                aux.append("EP")
                aux.append("EN")
            data.append(aux)
            aux = []
            if body['sp']:
                aux.append(str(sp[alumno]))
                aux.append(str(sn[alumno]))
            if body['ep']:
                aux.append(str(matrix12[str(alumno)]['EP']) + "%")
                aux.append(str(matrix12[str(alumno)]['EN']) + "%")
            data.append(aux)

            # ADD TABLE APARTADO 1
            addTablePdf(proposals, elements, data, style2, sLeft, alumno, bold=True, boldPreguntas=False, pos=False,
                        ap1=True, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False, ap12=False,
                        ap15=False, ap16=False, ap17=False, ap18=False, italic=False, matrices=False, data_matrix={},
                        spaceAfter=50, spaceBefore=30, colWidths=())

            data = []
            aux = []

            # ADD POSICION SOCIAL
            aux.append(gettext("POSICIÓN SOC"))
            data.append(aux)
            aux = []
            aux.append(position)
            data.append(aux)
            addTablePdf(proposals, elements, data, style2, sLeft, alumno, bold=False, boldPreguntas=False, pos=True,
                        ap1=False,
                        ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False, ap12=False, ap15=False,
                        ap16=False, ap17=False, ap18=False, italic=False, matrices=False, data_matrix={}, spaceAfter=50,
                        spaceBefore=30, colWidths=())

        # ADD APARTADO 2 ESTATUS POSITIVO Y POPULARIDAD SP Y NP
        if body['sp']:
            s.fontSize = 12
            if body['sp'] and body['np']:
                elements.append(Paragraph(gettext("2.- ESTATUS POSITIVO (SP) Y NIVEL MEDIO DE POPULARIDAD (NP)"), s))
            else:
                elements.append(Paragraph(gettext("2.- ESTATUS POSITIVO (SP)"), s))

            s.fontSize = 9

            data = []
            aux = []

            aux.append(gettext("NIVEL SP"))
            if body['np']:
                aux.append(gettext("VALOR NP"))
            data.append(aux)

            aux = []
            aux.append(str(proposals['sp'][alumno][list(proposals['sp'][alumno])[0]]))
            if body['np']:
                aux.append(str(np[alumno]) + "%")
            data.append(aux)

            # ADD TABLA APARTADO 2
            addTablePdf(proposals, elements, data, style2, sLeft, alumno, bold=True, boldPreguntas=False, pos=False,
                        ap1=False, ap2=True, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False, ap12=False,
                        ap15=False, ap16=False, ap17=False, ap18=False, italic=False, matrices=False, data_matrix={},
                        spaceAfter=50, spaceBefore=30, colWidths=())

        # ADD APARTADO 3 ESTATUS NEGATIVO Y RECHAZO SN Y NN
        if body['sp']:
            s.fontSize = 12
            if body['sp'] and body['np']:
                elements.append(Paragraph(gettext("3.- ESTATUS NEGATIVO (SN) Y NIVEL MEDIO DE RECHAZO (NN)"), s))
            else:
                elements.append(Paragraph(gettext("3.- ESTATUS NEGATIVO (SN)"), s))
            s.fontSize = 9

            data = []
            aux = []

            aux.append(gettext("NIVEL SN"))
            if body['np']:
                aux.append(gettext("VALOR NN"))
            data.append(aux)

            aux = []
            aux.append(str(proposals['sn'][alumno][list(proposals['sn'][alumno])[0]]))
            if body['np']:
                aux.append(str(nn[alumno]) + "%")
            data.append(aux)

            # ADD TABLE APARTADO 3
            addTablePdf(proposals, elements, data, style2, sLeft, alumno, bold=True, boldPreguntas=False, pos=False,
                        ap1=False, ap2=False, ap3=True, ap4=False, ap7=False, ap8=False, ap11=False, ap12=False,
                        ap15=False, ap16=False, ap17=False, ap18=False, italic=False, matrices=False, data_matrix={},
                        spaceAfter=50, spaceBefore=30, colWidths=())

        if body['rp']:
            # ADD APARTADO 4 AMISTADES RP
            s.fontSize = 12
            elements.append(Paragraph(gettext("4.- AMISTADES (RP)"), s))
            s.fontSize = 9

            # TABLA RELACIONES DE AMISTAD RECIPROCA
            data = []
            aux = []

            aux.append(gettext("NOMBRE"))
            aux.append(gettext("GRADO"))
            data.append(aux)

            for amigo in rp:
                aux = []
                aux.append(amigo.nombre + " " + amigo.apellidos)
                aux.append(str(rp[amigo][1]) + "-" + str(rp[amigo][2]))
                aux.append(rp[amigo][0])
                data.append(aux)

            # ALUMNO NO TIENE AMISTADES
            if len(rp) == 0:
                aux = []
                aux.append(str(gettext("No hay")))
                data.append(aux)

            addTablePdf(proposals, elements, data, style2, sLeft, alumno, bold=True, boldPreguntas=False, pos=False,
                        ap1=False, ap2=False, ap3=False, ap4=True, ap7=False, ap8=False, ap11=False, ap12=False,
                        ap15=False, ap16=False, ap17=False, ap18=False, italic=False, matrices=False, data_matrix={},
                        spaceAfter=50, spaceBefore=30, colWidths=())

            # ADD APARTADO 5 ENEMISTADES RN
            s.fontSize = 12
            elements.append(Paragraph(gettext("5.- ENEMISTADES (RN)"), s))
            s.fontSize = 9

            # ADD TABLA RELACIONES DE ENEMISTAD RECIPROCA
            data = []
            aux = []

            aux.append(gettext("NOMBRE"))
            aux.append(gettext("GRADO"))
            data.append(aux)

            for amigo in rn:
                aux = []
                aux.append(amigo.nombre + " " + amigo.apellidos)
                aux.append(str(rn[amigo][1]) + "-" + str(rn[amigo][2]))
                aux.append(rn[amigo][0])
                data.append(aux)

            # ALUMNO NO TIENE ENEMISTADES
            if len(rn) == 0:
                aux = []
                aux.append(str(gettext("No hay")))
                data.append(aux)

            addTablePdf(proposals, elements, data, style2, sLeft, alumno, bold=True, boldPreguntas=False, pos=False,
                        ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False, ap12=False,
                        ap15=False, ap16=False, ap17=False, ap18=False, italic=False, matrices=False, data_matrix={},
                        spaceAfter=50, spaceBefore=30, colWidths=())

        # ADD APARTADO 6 OPOSICION DE SENTIMIENTO OS
        if body['os']:
            s.fontSize = 12
            elements.append(Paragraph(gettext("6.- OPOSICIÓN DE SENTIMIENTO (OS)"), s))
            s.fontSize = 9

            # ADD TABLA RELACIONES OPUESTAS
            data = []
            aux = []

            aux.append(gettext("ELIGE"))
            aux.append(gettext("RECHAZA"))
            aux.append(gettext("GRADO"))
            data.append(aux)

            for amigo in os:
                aux = []
                aux.append(os[amigo][3].nombre + " " + os[amigo][3].apellidos)
                aux.append(os[amigo][4].nombre + " " + os[amigo][4].apellidos)
                aux.append(str(os[amigo][1]) + "-" + str(os[amigo][2]))
                aux.append(os[amigo][0])
                data.append(aux)

            # ALUMNO NO TIENE RELACIONES OPUESTAS
            if len(os) == 0:
                aux = []
                aux.append(str(gettext("No hay")))
                data.append(aux)

            addTablePdf(proposals, elements, data, style2, sLeft, alumno, bold=True, boldPreguntas=False, pos=False,
                        ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False, ap12=False,
                        ap15=False, ap16=False, ap17=False, ap18=False, italic=False, matrices=False, data_matrix={},
                        spaceAfter=50, spaceBefore=30, colWidths=())

        # ADD APARTADO 7 SOCIABILIDAD EP
        if body['ep']:
            s.fontSize = 12
            elements.append(Paragraph(gettext("7.- GRADO DE SOCIABILIDAD O EXPANSIVIDAD (EP)"), s))
            s.fontSize = 9

            data = []
            aux = []

            aux.append(gettext("VALOR EP"))
            aux.append(gettext("NIVEL EP"))
            data.append(aux)

            aux = []
            aux.append(str(matrix12[str(alumno)]['EP']) + "%")
            aux.append(str(proposals['ep'][alumno][list(proposals['ep'][alumno])[0]]))
            data.append(aux)

            # ADD TABLE APARTADO 7
            addTablePdf(proposals, elements, data, style2, sLeft, alumno, bold=True, boldPreguntas=False, pos=False,
                        ap1=False, ap2=False, ap3=False, ap4=False, ap7=True, ap8=False, ap11=False, ap12=False,
                        ap15=False, ap16=False, ap17=False, ap18=False, italic=False, matrices=False, data_matrix={},
                        spaceAfter=50, spaceBefore=30, colWidths=())

        # ADD APARTADO 8 EXPECTATIVA DE SER ELEGIDO PP
        if body['pp']:
            s.fontSize = 12
            elements.append(Paragraph(gettext("8.- EXPECTATIVA DE SER ELEGIDO (PP)"), s))
            s.fontSize = 9

            data = []
            aux = []

            aux.append(gettext("VALOR PP"))
            aux.append(gettext("NIVEL PP"))
            data.append(aux)
            aux = []
            aux.append(str(matrix34[str(alumno)]['PP']) + "%")
            aux.append(str(proposals['pp'][alumno][list(proposals['pp'][alumno])[0]]))
            data.append(aux)

            # ADD TABLA APARTADO 8
            addTablePdf(proposals, elements, data, style2, sLeft, alumno, bold=True, boldPreguntas=False, pos=False,
                        ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=True, ap11=False, ap12=False,
                        ap15=False, ap16=False, ap17=False, ap18=False, italic=False, matrices=False, data_matrix={},
                        spaceAfter=50, spaceBefore=30, colWidths=())

        # ADD APARTADO 9 ACIERTO EN SER ELEGIDO PAP
        # if body['pap']: #TODO SEPARAR O NO
            s.fontSize = 12
            elements.append(Paragraph(gettext("9.- GRADO DE ACIERTO EN LA EXPECTATIVA DE SER ELEGIDO (PAP)"), s))
            s.fontSize = 9

            data = []
            aux = []

            aux.append(gettext("VALOR PAP"))
            aux.append(gettext("NIVEL PAP"))
            data.append(aux)

            aux = []
            aux.append(str(matrix34[str(alumno)]['PAP']) + "%")
            aux.append(str(proposals['pap'][alumno][list(proposals['pap'][alumno])[0]]))
            data.append(aux)

            # ADD TABLE APARTADO 9
            addTablePdf(proposals, elements, data, style2, sLeft, alumno, bold=True, boldPreguntas=False, pos=False,
                        ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False, ap12=False,
                        ap15=False, ap16=False, ap17=False, ap18=False, italic=False, matrices=False, data_matrix={},
                        spaceAfter=50, spaceBefore=30, colWidths=())

        # ADD APARTADO 10 OIP
        if body['oip']:
            s.fontSize = 12
            elements.append(Paragraph(
                gettext("10.- OPOSICIÓN ENTRE LA EXPECTATIVA DE SER ELEGIDO Y LA REALIDAD DE SER RECHAZADO (OIP)"), s))
            s.fontSize = 9

            # ADD TABLA DE OPOSICION DE EXPECTATIVAS
            data = []
            aux = []

            aux.append(gettext("NOMBRE"))
            aux.append(gettext("GRADO"))
            data.append(aux)

            for amigo in oip:
                aux = []
                aux.append(amigo.nombre + " " + amigo.apellidos)
                aux.append(str(oip[amigo][1]) + "-" + str(oip[amigo][2]))
                aux.append(oip[amigo][0])
                data.append(aux)

            # ALUMNO NO TIENE OPOSICION
            if len(oip) == 0:
                aux = []
                aux.append(str(gettext("No hay")))
                data.append(aux)

            # ADD TABLE APARTADO 10
            addTablePdf(proposals, elements, data, style2, sLeft, alumno, bold=True, boldPreguntas=False, pos=False,
                        ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False, ap12=False,
                        ap15=False, ap16=False, ap17=False, ap18=False, italic=False, matrices=False, data_matrix={},
                        spaceAfter=50, spaceBefore=30, colWidths=())

        # ADD APARTADO 11 ANTIPATIA EN
        if body['ep']:
            s.fontSize = 12
            elements.append(Paragraph(gettext("11.- GRADO DE ANTIPATÍA (EN)"), s))
            s.fontSize = 9

            data = []
            aux = []

            aux.append(gettext("VALOR EN"))
            aux.append(gettext("NIVEL EN"))
            data.append(aux)

            aux = []
            aux.append(str(matrix12[str(alumno)]['EN']) + "%")
            aux.append(str(proposals['en'][alumno][list(proposals['en'][alumno])[0]]))
            data.append(aux)

            # ADD TABLE APARTADO 11
            addTablePdf(proposals, elements, data, style2, sLeft, alumno, bold=True, boldPreguntas=False, pos=False,
                        ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=True, ap12=False,
                        ap15=False, ap16=False, ap17=False, ap18=False, italic=False, matrices=False, data_matrix={},
                        spaceAfter=50, spaceBefore=30, colWidths=())

        # ADD APARTADO 12 EXPECTATIVA DE RECHAZO PN
        if body['pp']:
            s.fontSize = 12
            elements.append(Paragraph(gettext("12.- EXPECTATIVA DE SER RECHAZADO (PN)"), s))
            s.fontSize = 9

            data = []
            aux = []

            aux.append(gettext("VALOR PN"))
            aux.append(gettext("NIVEL PN"))
            data.append(aux)

            aux = []
            aux.append(str(matrix34[str(alumno)]['PN']) + "%")
            aux.append(str(proposals['pn'][alumno][list(proposals['pn'][alumno])[0]]))
            data.append(aux)

            # ADD TABLE APARTADO 12
            addTablePdf(proposals, elements, data, style2, sLeft, alumno, bold=True, boldPreguntas=False, pos=False,
                        ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False, ap12=True,
                        ap15=False, ap16=False, ap17=False, ap18=False, italic=False, matrices=False, data_matrix={},
                        spaceAfter=50, spaceBefore=30, colWidths=())

        # ADD APARTADO ACIERTO EXPECTATIVA DE RECHAZO PAN
        #if body['pap']: #TODO SEPARAR O NO
            s.fontSize = 12
            elements.append(Paragraph(gettext("13.- GRADO DE ACIERTO EN LA EXPECTATIVA DE SER RECHAZADO (PAN)"), s))
            s.fontSize = 9

            data = []
            aux = []

            aux.append(gettext("VALOR PAN"))
            aux.append(gettext("NIVEL PAN"))
            data.append(aux)

            aux = []
            aux.append(str(matrix34[str(alumno)]['PAN']) + "%")
            aux.append(str(proposals['pan'][alumno][list(proposals['pan'][alumno])[0]]))
            data.append(aux)

            # ADD TABLE APARTADO 13
            addTablePdf(proposals, elements, data, style2, sLeft, alumno, bold=True, boldPreguntas=False, pos=False,
                        ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False, ap12=False,
                        ap15=False, ap16=False, ap17=False, ap18=False, italic=False, matrices=False, data_matrix={},
                        spaceAfter=50, spaceBefore=30, colWidths=())

        # ADD APARTADO 14 OIN
        if body['oip']:
            s.fontSize = 12
            elements.append(Paragraph(
                gettext("14.- OPOSICIÓN ENTRE LA EXPECTATIVA DE SER RECHAZADO A LA REALIDAD DE SER ELEGIDO (OIN)"), s))
            s.fontSize = 9

            # ADD TABLA DE OPOSICION DE EXPECTATIVA DE RECHAZO
            data = []
            aux = []

            aux.append(gettext("NOMBRE"))
            aux.append(gettext("GRADO"))
            data.append(aux)

            for amigo in oin:
                aux = []
                aux.append(amigo.nombre + " " + amigo.apellidos)
                aux.append(str(oin[amigo][1]) + "-" + str(oin[amigo][2]))
                aux.append(oin[amigo][0])
                data.append(aux)

            if len(oin) == 0:
                aux = []
                aux.append(str(gettext("No hay")))
                data.append(aux)

            # ADD TABLE APARTADO 14
            addTablePdf(proposals, elements, data, style2, sLeft, alumno, bold=True, boldPreguntas=False, pos=False,
                        ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False, ap12=False,
                        ap15=False, ap16=False, ap17=False, ap18=False, italic=False, matrices=False, data_matrix={},
                        spaceAfter=50, spaceBefore=30, colWidths=())

        if body['ip']:
            # ADD APARTADO 15 IMPRESION DEL GRUPO DE SER ELEGIDO IP IMP
            s.fontSize = 12
            elements.append(
                Paragraph(gettext("15.- IMPRESIÓN QUE TIENE EL GRUPO DE SER ELEGIDO POR EL/ELLA (IP E IMP)"), s))
            s.fontSize = 9

            data = []
            aux = []

            aux.append(gettext("VALOR IP"))
            aux.append(gettext("NIVEL IP"))
            if body['imp']:
                aux.append(gettext("VALOR IMP"))
                aux.append(gettext("NIVEL IMP"))
            data.append(aux)

            aux = []
            aux.append(str(ip[alumno]))
            aux.append(str(proposals['ip'][alumno][list(proposals['ip'][alumno])[0]]))
            if body['imp']:
                aux.append(str(imp[alumno]) + "%")
                aux.append(str(proposals['imp'][alumno][list(proposals['imp'][alumno])[0]]))
            data.append(aux)

            # ADD TABLE APARTADO 15
            addTablePdf(proposals, elements, data, style2, sLeft, alumno, bold=True, boldPreguntas=False, pos=False,
                        ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False, ap12=False,
                        ap15=True, ap16=False, ap17=False, ap18=False, italic=False, matrices=False, data_matrix={},
                        spaceAfter=50, spaceBefore=30, colWidths=())

            # ADD APARTADO 16 IMPRESION DEL GRUPO DE SER RECHAZADO IN IMN
            s.fontSize = 12
            elements.append(
                Paragraph(gettext("16.- IMPRESIÓN QUE TIENE EL GRUPO DE SER RECHAZADO POR EL/ELLA (IN E IMN)"), s))
            s.fontSize = 9

            data = []
            aux = []

            aux.append(gettext("VALOR IN"))
            aux.append(gettext("NIVEL IN"))
            if body['imp']:
                aux.append(gettext("VALOR IMN"))
                aux.append(gettext("NIVEL IMN"))
            data.append(aux)

            aux = []
            aux.append(str(iN[alumno]))
            aux.append(str(proposals['in'][alumno][list(proposals['in'][alumno])[0]]))
            if body['imp']:
                aux.append(str(imn[alumno]) + "%")
                aux.append(str(proposals['imn'][alumno][list(proposals['imn'][alumno])[0]]))
            data.append(aux)

            # ADD TABLE APARTADO 16
            addTablePdf(proposals, elements, data, style2, sLeft, alumno, bold=True, boldPreguntas=False, pos=False,
                        ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False, ap12=False,
                        ap15=False, ap16=True, ap17=False, ap18=False, italic=False, matrices=False, data_matrix={},
                        spaceAfter=50, spaceBefore=30, colWidths=())

        if body['ipp']:
            # ADD APARTADO 17 PREFERENCIA SOCIAL POSITIVA IPP
            s.fontSize = 12
            elements.append(Paragraph(gettext("17.- NIVEL DE PREFERENCIA SOCIAL POSITIVA (IPP): LÍDER"), s))
            s.fontSize = 9

            data = []
            aux = []

            aux.append(gettext("VALOR IPP"))
            aux.append(gettext("NIVEL IPP"))
            data.append(aux)

            aux = []
            aux.append(str(ipp[alumno]) + "%")
            aux.append(str(proposals['ipp'][alumno][list(proposals['ipp'][alumno])[0]]))
            data.append(aux)

            # ADD TABLE APARTADO 17
            addTablePdf(proposals, elements, data, style2, sLeft, alumno, bold=True, boldPreguntas=False, pos=False,
                        ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False, ap12=False,
                        ap15=False, ap16=False, ap17=True, ap18=False, italic=False, matrices=False, data_matrix={},
                        spaceAfter=50, spaceBefore=30, colWidths=())

            # ADD APARTADO 18 PREFERENCIA SOCIAL NEGATIVA IPN
            s.fontSize = 12
            elements.append(Paragraph(gettext("18.- NIVEL DE PREFERENCIA SOCIAL NEGATIVA (IPN): PESADO"), s))
            s.fontSize = 9

            data = []
            aux = []

            aux.append(gettext("VALOR IPN"))
            aux.append(gettext("NIVEL IPN"))
            data.append(aux)

            aux = []
            aux.append(str(ipn[alumno]) + "%")
            aux.append(str(proposals['ipn'][alumno][list(proposals['ipn'][alumno])[0]]))
            data.append(aux)

            # ADD TABLE APARTADO 18
            addTablePdf(proposals, elements, data, style2, sLeft, alumno, bold=True, boldPreguntas=False, pos=False,
                        ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False, ap12=False,
                        ap15=False, ap16=False, ap17=False, ap18=True, italic=False, matrices=False, data_matrix={},
                        spaceAfter=50, spaceBefore=30, colWidths=())

        # CAMBIO DE PAGINA
        elements.append(PageBreak())
        doc.pagesize = portrait(A4)

        # PROPUESTA DE INTERVENCION
        s.fontSize = 11
        elements.append(Paragraph(gettext("Propuesta de intervención"), s))

        # TITULO DE AREAS
        s.fontSize = 10
        elements.append(Paragraph(gettext("Áreas"), s))

        elements.append(Spacer(1, 0.1 * inch))
        d = Drawing(760, 1)
        d.add(Line(0, 0, 500, 0))

        elements.append(d)
        elements.append(Spacer(1, 0.25 * inch))

        sLeft.textColor = 'black'
        listProposals = []
        for vari in proposals['recomendaciones']:
            if (not_empty(proposals['recomendaciones'][vari])):
                title = return_des(proposals['recomendaciones'][vari])
                listProposals.append(
                    ListItem(Paragraph(vari + ": " + title, sLeft),
                             spaceAfter=10))
                firstList = []
                for varinum in proposals['recomendaciones'][vari]:
                    for ex in proposals['recomendaciones'][vari][varinum]:
                        if (not_empty_ex(proposals['recomendaciones'][vari][varinum][ex])):
                            firstList.append(ListItem(Paragraph(ex, sLeft), spaceAfter=10))
                            secondList = []
                            for num in proposals['recomendaciones'][vari][varinum][ex]:
                                for secondArea in proposals['recomendaciones'][vari][varinum][ex][num]:
                                    if len(proposals['recomendaciones'][vari][varinum][ex][num][secondArea]):
                                        secondList.append(ListItem(Paragraph("<link href='" + return_link(proposals['recomendaciones'][vari][varinum][ex][num][secondArea]) + "' color='blue'><u>" + secondArea + "</u></link>", sLeft), spaceAfter=10)) #link
                                        students = []
                                        for studentProp in proposals['recomendaciones'][vari][varinum][ex][num][
                                            secondArea]:
                                            students.append(ListItem(Paragraph(studentProp, sLeft), spaceAfter=10))
                                            reasonsList = []
                                            for i, reasons in enumerate(
                                                    proposals['recomendaciones'][vari][varinum][ex][num][secondArea][
                                                        studentProp]):
                                                if i != 0 and reasons != title:
                                                    reasonsList.append(ListItem(Paragraph(reasons, sLeft)))
                                            students.append(ListItem(
                                                ListFlowable(reasonsList, bulletType='bullet', start='diamond',
                                                             leftIndent=10,
                                                             bulletFontSize=7, bulletOffsetY=-2), bulletColor="white",
                                                spaceAfter=15))
                                        secondList.append(ListItem(
                                            ListFlowable(students, bulletType='bullet', start='squarelrs',
                                                         leftIndent=10,
                                                         bulletFontSize=7, bulletOffsetY=-2), bulletColor="white",
                                            spaceAfter=15))
                            firstList.append(ListItem(
                                ListFlowable(secondList, bulletType='bullet', start='rarrowhead', leftIndent=10,
                                             bulletFontSize=7, bulletOffsetY=-2), bulletColor="white", spaceAfter=15))
                listProposals.append(ListItem(
                    ListFlowable(firstList, bulletType='bullet', start='square', leftIndent=10, bulletFontSize=5,
                                 bulletOffsetY=-3), bulletColor="white", spaceAfter=20))
        t = ListFlowable(listProposals, bulletType='bullet', bulletOffsetY=2)

        elements.append(t)

        if all == 1:
            return elements
        else:
            doc.multiBuild(elements, canvasmaker=FooterCanvas)
            pdfPrint = buffer.getvalue()
            buffer.close()
            response = make_response(pdfPrint)
            response.headers.set('Content-Disposition', 'attachment',
                                 filename="Informe-Completo-Alumno-{0}-Cuestionario-{1}.pdf".format(
                                     studentCurrent[2].nombre + " " + studentCurrent[2].apellidos, test.nombre))
            response.headers.set('Content-Type', 'application/pdf')
            db.session.close()
            return response
    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)


def show_results_student(request, pdf, all, alumno=None):
    try:
        body = request.get_json()

        if not all:
            alumno = body['alumno']
        user_id = get_jwt_identity()
        teacher = db.session.query(Profesor, User).join(User, and_(Profesor.user == user_id,
                                                                   Profesor.user == User.id, )).one()
        preferencias = Preferencias.query.filter(Preferencias.user == user_id).one().serialize
        body = {**body, **preferencias}
        test = Test.query.get(body['test'])
        preguntas = test.preguntas
        alumnos = db.session.query(Alumno, AlumnosTest.c.code, User.nombre, User.apellidos, User.fecha_nacimiento, AlumnosClase.c.clase, AlumnosClase.c.alias).join(AlumnosTest,
                                                                                                 and_(
                                                                                                     test.id == AlumnosTest.c.test,
                                                                                                     AlumnosTest.c.alumno == Alumno.id, )) \
            .join(User, User.id == Alumno.user).join(AlumnosClase, and_(AlumnosClase.c.alumno == Alumno.id, AlumnosClase.c.clase == test.clase)).all()
        als = {}
        for a in alumnos:
            als[a[2] + " " + a[3]] = str(a[1])
        studentCurrent = db.session.query(Alumno, AlumnosTest.c.code, User, AlumnosClase.c.alias).join(AlumnosTest,
                                                                                 and_(
                                                                                     alumno == AlumnosTest.c.code,
                                                                                     AlumnosTest.c.alumno == Alumno.id, )) \
            .join(User, User.id == Alumno.user).join(AlumnosClase, and_(AlumnosClase.c.alumno == Alumno.id, AlumnosClase.c.clase == test.clase)).one()
        matrix = {}
        matrixText = {}
        createMatrix(test, preguntas, alumnos, matrix, matrixText, "no")

        # DECLARAR VARIABLES
        sp, spval, np, sn, snval, nn, ip, ipval, imp, iN, inval, imn, ipp, ipval5, ipn, inval6, matrix12, matrix34 = {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}
        # ic, id = 0, 0

        # INICIALIZAR VARIABLES
        processAnswersMatrix(body, matrix, matrix12, matrix34, sp, spval, sn, snval, ip, ipval, iN, inval, ipp,
                             ipval5, ipn, inval6, "no", False)

        num_alumnos = len(alumnos)

        # if body['spv'] and body['np']:
        #     calculateNpNn(np, nn, spval, snval, num_alumnos)
        #
        # if body['ipv']:
        #     calculateImpImnIppIpn(imp, imn, ipp, ipn, ipval, inval, ipval5, inval6, num_alumnos, body['ipp'],
        #                           body['imp'])

        matrix12aux = copy.deepcopy(matrix12)
        matrix34aux = copy.deepcopy(matrix34)

        # if body['ic']:
        #     ic, id = calculateGroupVariables(matrix12)

        # if body['pap']:
        #     calculatePapPanPpPn(matrix34, body['pp'])

        data1, data2, data3, data4 = {}, {}, {}, {}

        # CALCULAR LAS TABLAS DE DATOS
        calculateDataSP(data1, data2, sp, num_alumnos, sn)
        calculateDataIP(data3, data4, ip, num_alumnos, iN)

        clase = Clase.query.get(test.clase)

        # OBTENER RECOMENDACIONES
        proposals = get_proposals(sp, np, nn, sn, spval, snval, imp, ipval, imn, inval, iN, ip, ipp, ipval5, ipn,
                                  inval6, data1, data2, data3, data4, num_alumnos, matrix12aux, matrix34aux, matrix, alumno,
                                  matrixText,
                                  clase.grupo_edad, body)

        # OBTENER POSICION SOCIAL DEL ALUMNO
        position = get_soc(proposals['sp'][alumno], proposals['sn'][alumno],
                           proposals['ep'][alumno],
                           proposals['en'][alumno], np[alumno], nn[alumno])

        if pdf == 1:
            rp, rn, os = {}, {}, {}
            calculateRpRnOs(matrix, rp, rn, os, alumno, studentCurrent[0],0)

            oip, oin = {}, {}
            calculateOipOin(matrix, oip, oin, alumno,0)
            return producePdf(alumno, studentCurrent, test, matrix, preguntas, teacher, clase, matrixText,
                              sp, sn, matrix12,
                              matrix34, proposals, position, np, nn, rp, rn, os, oip, oin, ip, iN, ipp, ipn, imp,
                              imn, body, all)
        else:
            rp, rn, os = {}, {}, {}
            calculateRpRnOs(matrix, rp, rn, os, alumno, studentCurrent[1],1)
            oip, oin = {}, {}
            calculateOipOin(matrix, oip, oin, alumno,1)
            db.session.close()
            return jsonify({'teacher': {**teacher[0].serialize, **teacher[1].serialize},
                            'test': test.serialize,
                            'alumnos': [{**al[0].serialize(al[5], al[1]), 'nombre': " ".join(al[2].split()).strip(),
                                         'apellidos': " ".join(al[3].split()).strip(), 'fecha_nacimiento': al[4], 'alias': al[6]} for al in
                      alumnos],
                            'alumno': studentCurrent[0].serialize(studentCurrent[1]),
                            'respuestas': json.dumps(matrix),
                            'preguntas': [i.serialize for i in preguntas], 'sp': json.dumps(sp[alumno]),
                            'sn': json.dumps(sn[alumno]),
                            'ep': json.dumps(matrix12[str(alumno)]['EP']),
                            'en': json.dumps(matrix12[str(alumno)]['EN']), 'pos': position,
                            'spValue': proposals['sp'][alumno][list(proposals['sp'][alumno])[0]],
                            'np': json.dumps(np[alumno]),
                            'snValue': proposals['sn'][alumno][list(proposals['sn'][alumno])[0]],
                            'nn': json.dumps(nn[alumno]), 'rp': json.dumps(rp), 'rn': json.dumps(rn),
                            'os': json.dumps(os),
                            'epValue': proposals['ep'][alumno][list(proposals['ep'][alumno])[0]],
                            'pp': json.dumps(matrix34[str(alumno)]['PP']),
                            'pap': json.dumps(matrix34[str(alumno)]['PAP']),
                            'ppValue': proposals['pp'][alumno][list(proposals['pp'][alumno])[0]],
                            'papValue': proposals['pap'][alumno][list(proposals['pap'][alumno])[0]],
                            'enValue': proposals['en'][alumno][list(proposals['en'][alumno])[0]],
                            'pnValue': proposals['pn'][alumno][list(proposals['pn'][alumno])[0]],
                            'panValue': proposals['pan'][alumno][list(proposals['pan'][alumno])[0]],
                            'ippValue': proposals['ipp'][alumno][list(proposals['ipp'][alumno])[0]],
                            'ipnValue': proposals['ipn'][alumno][list(proposals['ipn'][alumno])[0]],
                            'pn': json.dumps(matrix34[str(alumno)]['PN']),
                            'pan': json.dumps(matrix34[str(alumno)]['PAN']),
                            'ipp': json.dumps(ipp[alumno]), 'ipn': json.dumps(ipn[alumno]),
                            'ip': json.dumps(ip[alumno]), 'in': json.dumps(iN[alumno]),
                            'ipValue': proposals['ip'][alumno][list(proposals['ip'][alumno])[0]],
                            'inValue': proposals['in'][alumno][list(proposals['in'][alumno])[0]],
                            'imp': json.dumps(imp[alumno]),
                            'impValue': proposals['imp'][alumno][list(proposals['imp'][alumno])[0]],
                            'imn': json.dumps(imn[alumno]),
                            'imnValue': proposals['imn'][alumno][list(proposals['imn'][alumno])[0]],
                            'oip': json.dumps(oip),
                            'oin': json.dumps(oin), 'recomendaciones': proposals['recomendaciones'],
                            'respuestasText2': matrixText[2][studentCurrent[1]],
                            'respuestasText4': matrixText[4][studentCurrent[1]],
                            'respuestasText6': matrixText[6][studentCurrent[1]]
                            })

    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)


def escala(level, variable, min=None, max=None):
    try:
        value = ""
        if level == 0:
            if variable >= 75:
                value = "Alto"
            elif 45 <= variable <= 74:
                value = "Medio"
            elif 25 <= variable <= 44:
                value = "Bajo"
            else:
                value = "Muy bajo"
        elif level == 1:
            if variable >= 75:
                value = "Muy Alto"
            elif 45 <= variable <= 74:
                value = "Alto"
            elif 25 <= variable <= 44:
                value = "Medio"
            else:
                value = "Bajo"
        elif level == 2:
            if variable >= min:
                value = {variable: gettext("Alto")}
            elif max <= variable < min:
                value = {variable: gettext("Medio")}
            else:
                value = {variable: gettext("Bajo")}
        elif level == 3:
            if variable >= 75:
                value = {variable: gettext("Alto")}
            elif 45 <= variable <= 74:
                value = {variable: gettext("Medio")}
            elif 25 <= variable <= 44:
                value = {variable: gettext("Bajo")}
            else:
                value = {variable: gettext("Muy bajo")}
        return value
    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)

def createGraph(matrixaux, alumnos, sp, sn, ip, iN, num):
    try:
        nodesFilterValues = {}
        nt = Network(height='650px', width='515px', directed=True)

        students = []
        for user in alumnos:
            aux = {}
            nodesFilterValues[alumnos[user]] = True
            aux['id'] = alumnos[user]
            aux['label'] = user
            aux['font'] = {
                'strokeWidth': 2,
                'strokeColor': "#ffffff"
            }
            if num == 1:
                aux['value'] = int(sp[alumnos[user]])
            elif num == 2:
                aux['value'] = int(sn[alumnos[user]])
            elif num == 3:
                aux['value'] = int(ip[alumnos[user]])
            elif num == 4:
                aux['value'] = int(iN[alumnos[user]])

            students.append(aux)
        for n in students:
            nt.add_node(n['id'], label=n['label'], value=int(n['value']), borderWidth=n['font']['strokeWidth'])

        relations = []
        relationsDone = {}
        for student1 in matrixaux[num]:
            for student2 in matrixaux[num][student1]:
                aux = {}
                aux['from'] = student1
                for color in matrixaux[num][student1][student2]:
                    if matrixaux[num][student1][student2][color] != '' and not (
                            student2 + student1 in relationsDone):
                        aux['to'] = student2
                        aux['value'] = matrixaux[num][student1][student2][color]
                        aux['color'] = color
                        if color == '#d6c22b':
                            aux['title'] = "Se eligen mutuamente"
                            aux['relation'] = "mutual"
                        elif color == "#e05ab8":
                            aux['title'] = "Oposición de sentimiento"
                            aux['relation'] = "os"
                        elif color == "#0da863":
                            aux['title'] = "Se rechazan mutuamente"
                            aux['relation'] = "reject"
                        elif color == "#349beb":
                            aux['title'] = "Cree que lo eligen y acierta"
                            aux['relation'] = "believe"
                        elif color == "#ed3e46":
                            aux[
                                'title'] = "Oposición entre la expectativa de ser elegido y la realidad de ser rechazado"
                            aux['relation'] = "oip"
                        elif color == "#eb8034":
                            aux['title'] = "Cree que lo rechazan y acierta"
                            aux['relation'] = "believeNo"
                        elif color == "#9646e0":
                            aux[
                                'title'] = "Oposición entre la expectativa de ser rechazado y la realidad de ser elegido"
                            aux['relation'] = "oin"
                        else:
                            aux['relation'] = "normal"

                        if student2 in matrixaux[num]:
                            if student1 in matrixaux[num][student2]:
                                for color2 in matrixaux[num][student2][student1]:
                                    if matrixaux[num][student2][student1][color2] != '' and color == color2:
                                        aux['physics'] = False
                                        relationsDone[student1 + student2] = 1
                                        if (int(matrixaux[num][student2][student1][color2]) == 5 or
                                            int(matrixaux[num][student2][student1][color2]) == 4) and (
                                                int(matrixaux[num][student1][student2][color]) == 5 or
                                                int(matrixaux[num][student1][student2][color]) == 4):
                                            aux['value'] = 5
                                        elif int(matrixaux[num][student2][student1][color2]) == 3 or \
                                                int(matrixaux[num][student1][student2][color]) == 3 or (
                                                int(matrixaux[num][student1][student2][color]) == 2 and
                                                int(matrixaux[num][student2][student1][color2]) == 4) or (
                                                int(matrixaux[num][student2][student1][color2]) == 2 and
                                                int(matrixaux[num][student1][student2][color]) == 4):
                                            aux['value'] = 3
                                        elif abs(int(matrixaux[num][student1][student2][color]) -
                                                 int(matrixaux[num][student2][student1][color2])) >= 2:
                                            aux['value'] = 3
                                            aux['dashes'] = True
                                            aux['title'] = aux['title'] + "\nElección recíproca desequilibrada"
                                        else:
                                            aux['value'] = 1

                                    else:
                                        aux['physics'] = True
                        else:
                            aux['physics'] = True
                        relations.append(aux)
                        if not aux['physics']:
                            aux2 = copy.deepcopy(aux)
                            aux2['to'] = aux['from']
                            aux2['from'] = aux['to']
                            relations.append(aux2)

        # create an array with edges
        for e in relations:  # TODO COLOR, DASHES, RELATION, TITLE
            nt.add_edge(e['from'], e['to'], width=1 / ((math.log(int(e['value']) / 5)) * -5 + 0.5) + 1.5,
                        color=e['color'],
                        physics=e['physics'])

        nt.set_edge_smooth('dynamic')
        options = {'physics': {
            'barnesHut': {
                'gravitationalConstant': -2000,
                'centralGravity': 0.3,
                'springLength': 300,
                'springConstant': 0.04,
                'damping': 0.09,
                'avoidOverlap': 0
            },
            'forceAtlas2Based': {
                'gravitationalConstant': -50,
                'centralGravity': 0.01,
                'springConstant': 0.08,
                'springLength': 300,
                'damping': 0.4,
                'avoidOverlap': 0
            },
            'repulsion': {
                'centralGravity': 0.2,
                'springLength': 500,
                'springConstant': 0.05,
                'nodeDistance': 500,
                'damping': 0.09
            },
            'hierarchicalRepulsion': {
                'centralGravity': 0.0,
                'springLength': 500,
                'springConstant': 0.01,
                'nodeDistance': 500,
                'damping': 0.09,
                'avoidOverlap': 0
            }
        }}
        nt.set_options(json.dumps(options))
        fileNames = []
        htmlName = str(uuid.uuid4()) + '.html'
        fileNames.append(htmlName)
        nt.write_html(htmlName)
        hti = Html2Image()
        imageName = str(uuid.uuid4())
        hti.screenshot(html_file=htmlName, save_as=imageName + "-" + str(num) + ".png")
        fileNames.append(imageName + "-" + str(num) + ".png")
        im = Image.open(imageName + "-" + str(num) + ".png")
        im2 = im.crop(im.getbbox())
        im2.save(imageName + "Cropped-" + str(num) + ".png")
        fileNames.append(imageName + "Cropped-" + str(num) + ".png")
        return fileNames
    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)


def producePdfComplete(test, matrixaux, respuestasNum, teacher, clase, sp, sn, matrix12,
                       matrix34,
                       proposals, np, nn, os, oip, oin, ip, iN, ipp, ipn, imp, imn, body, alumnos, alumnosInitials, als,
                       data1, data2, data3, data4, spval,
                       snval, ipval, inval, titlematrix12, titlematrix34, mutual, reject, believe, believeNo):
    try:
        # INICIALIZAR PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=100, bottomMargin=50)
        doc.pagesize = portrait(A4)
        elements = []

        # CONFIGURAR ESTILO ALINEACION CENTRADA
        s = getSampleStyleSheet()
        s = s['BodyText']
        s.wordWrap = 'CJK'
        s.fontName = 'Helvetica'
        s.alignment = 1

        # FONT SIZE TITULO
        s.fontSize = 20
        # TITULO
        title = Paragraph(gettext("Informe de grupo {0}".format(clase.nombre)), s)
        elements.append(title)

        # FONT SIZE TEXTO
        s.fontSize = 10

        # CONFIGURAR ESTILO ALINEACION IZQUIERDA
        sLeft = getSampleStyleSheet()
        sLeft = sLeft['BodyText']
        sLeft.wordWrap = 'CJK'
        sLeft.fontName = 'Helvetica'
        sLeft.alignment = 0
        sLeft.fontSize = 10

        data = []

        colegio = Colegio.query.get(teacher[1].colegio)
        addLinePdf(data, colegio.nombre, gettext("Colegio"))

        addLinePdf(data, clase.nombre, gettext("Curso y Grupo"))

        addLinePdf(data, teacher[1].nombre + " " + teacher[1].apellidos,
                   gettext(gettext("Tutor responsable")))

        addLinePdf(data, test.nombre, gettext("Nombre del test"))

        addLinePdf(data, str(test.date_created.strftime('%d/%m/%Y %H:%M')), gettext("Fecha de creación del test"))

        # ADD TABLE
        addTablePdf(proposals, elements, data, style1, sLeft, None, bold=False, boldPreguntas=False, pos=False,
                    ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False, ap12=False,
                    ap15=False, ap16=False, ap17=False, ap18=False, italic=True, matrices=False, data_matrix={},
                    spaceAfter=50, spaceBefore=50, colWidths=())

        # ADD ALUMNOS
        s.fontSize = 11
        elements.append(Paragraph(gettext("Alumnos"), s))

        s.fontSize = 10
        data = []
        aux = []
        aux.append(gettext('Código'))
        aux.append(gettext('Nombre'))
        aux.append(gettext('Responde'))
        data.append(aux)

        aux = []
        for al in alumnos:
            for a in alumnosInitials:
                if alumnosInitials[a][1] == al[1]:
                    aux.append(a)
                    aux.append(alumnosInitials[a][2] + " " + alumnosInitials[a][3])
                    if alumnosInitials[a][4]:
                        aux.append(gettext('Sí'))
                    else:
                        aux.append(gettext('No'))
                    data.append(aux)
                    aux = []

        addTablePdf(proposals, elements, data, style3, sLeft, None, bold=True, boldPreguntas=False, pos=False,
                    ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False, ap12=False,
                    ap15=False, ap16=False, ap17=False, ap18=False, italic=True, matrices=False, data_matrix={},
                    spaceAfter=50, spaceBefore=25, colWidths=())

        # ADD LEYENDA
        style = copy.deepcopy(style4)
        s.fontSize = 11
        elements.append(Paragraph(gettext("Leyenda de Colores"), s))

        s.fontSize = 10
        data = []
        aux = []
        aux.append(gettext('Significado'))
        aux.append(gettext('Color'))
        data.append(aux)

        aux = [gettext('Se eligen mutuamente'),'']
        data.append(aux)
        style.append(
            ('BACKGROUND', (1, 1), (1, 1), colors.HexColor('#d6c22b'))) #amarillo

        aux = [gettext('Oposición de sentimiento (OS)'), '']
        data.append(aux)
        style.append(
            ('BACKGROUND', (1, 2), (1, 2), colors.HexColor('#e05ab8'))) #rosa

        aux = [gettext('Se rechazan mutuamente'), '']
        data.append(aux)
        style.append(
            ('BACKGROUND', (1, 3), (1, 3), colors.HexColor('#0da863'))) #verde

        aux = [gettext('Cree que lo eligen y acierta'), '']
        data.append(aux)
        style.append(
            ('BACKGROUND', (1, 4), (1, 4), colors.HexColor('#349beb'))) #azul

        aux = [gettext('Oposición entre la expectativa de ser elegido y la realidad de ser rechazado (OIP)'), '']
        data.append(aux)
        style.append(
            ('BACKGROUND', (1, 5), (1, 5), colors.HexColor('#ed3e46'))) #rojo

        aux = [gettext('Cree que lo rechazan y acierta'), '']
        data.append(aux)
        style.append(
            ('BACKGROUND', (1, 6), (1, 6), colors.HexColor('#eb8034'))) #naranja

        aux = [gettext('Oposición entre la expectativa de ser rechazado y la realidad de ser elegido (OIN)'), '']
        data.append(aux)
        style.append(
            ('BACKGROUND', (1, 7), (1, 7), colors.HexColor('#9646e0'))) #violeta

        addTablePdf(proposals, elements, data, style, sLeft, None, bold=True, boldPreguntas=False, pos=False,
                    ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False, ap12=False,
                    ap15=False, ap16=False, ap17=False, ap18=False, italic=True, matrices=False, data_matrix={},
                    spaceAfter=50, spaceBefore=25, colWidths=())

        # ADD PREGUNTAS
        elements.append(PageBreak())

        s.fontSize = 11
        elements.append(Paragraph(gettext("Preguntas"), s))

        elements.append(Spacer(1, 0.1 * inch))

        style = copy.deepcopy(style4)
        data = []
        aux = []
        row = 0
        col = 0
        fileNames = []
        for question in respuestasNum:
            aux.append(str(question) + '#')
            for al in alumnos:
                for a in alumnosInitials:
                    if alumnosInitials[a][1] == al[1]:
                        aux.append(a)
            data.append(aux)
            row += 1
            aux = []
            for questionName in respuestasNum[question]:
                title = Paragraph(questionName, s)
                elements.append(title)
                for al in alumnos:
                    for a in alumnosInitials:
                        if alumnosInitials[a][1] == al[1]:
                            for studentAnswer in respuestasNum[question][questionName]:
                                if studentAnswer == alumnosInitials[a][1]:
                                    aux.append(a)
                                    col += 1
                                    for al2 in alumnos:
                                        for answers in respuestasNum[question][questionName][studentAnswer]:
                                            if answers == al2[1]:
                                                for an in respuestasNum[question][questionName][studentAnswer][
                                                    answers]:
                                                    aux.append(respuestasNum[question][questionName][studentAnswer][
                                                                   answers][an])
                                                    style.append(
                                                        ('BACKGROUND', (col, row), (col, row), colors.HexColor(an)))
                                                    col += 1
                                    data.append(aux)
                                    row += 1
                                    col = 0
                                    aux = []

            addTablePdf(proposals, elements, data, style, sLeft, None, bold=True, boldPreguntas=False, pos=False,
                        ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False, ap12=False,
                        ap15=False, ap16=False, ap17=False, ap18=False, italic=True, matrices=False, data_matrix={},
                        spaceAfter=50, spaceBefore=20, colWidths=())

            style = copy.deepcopy(style4)
            data = []
            aux = []
            row = 0
            col = 0

            if question < 5:
                elements.append(PageBreak())

                s.fontSize = 11
                elements.append(Paragraph(gettext("Grafo Pregunta ") + str(question), s))
                elements.append(Spacer(1, 0.1 * inch))

                listNames = createGraph(matrixaux, als, sp, sn, ip, iN, question)
                fileNames = fileNames + listNames
                elements.append(reportlab.platypus.Image(listNames[2]))
                elements.append(PageBreak())

        # ADD MATRICES DE PREGUNTAS
        s.fontSize = 11
        elements.append(Paragraph(gettext("Cálculo de variables"), s))

        if body['sp']:
            s.fontSize = 10
            elements.append(Paragraph(gettext("Matriz pregunta tipo 1"), s))

            aux.append('#')
            colWidths = (10 * mm,)
            for al in alumnos:
                for a in alumnosInitials:
                    if alumnosInitials[a][1] == al[1]:
                        aux.append(a)
                        colWidths = colWidths + (None,)
            data.append(aux)
            aux = []
            aux.append("SP")
            for a in alumnos:
                for spuser in sp:
                    if spuser == a[1]:
                        aux.append(str(sp[spuser]))
            data.append(aux)

            if body['spv']:
                aux = []
                aux.append("SP val")
                for a in alumnos:
                    for spuser in spval:
                        if spuser == a[1]:
                            aux.append(str(spval[spuser]))
                data.append(aux)

            if body['np']:
                aux = []
                aux.append("NP")
                for a in alumnos:
                    for spuser in np:
                        if spuser == a[1]:
                            aux.append(str(np[spuser]) + "%")
                data.append(aux)

            data1['group'] = 1
            addTablePdf(proposals, elements, data, style4, sLeft, None, bold=False, boldPreguntas=False, pos=False,
                        ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False, ap12=False,
                        ap15=False, ap16=False, ap17=False, ap18=False, italic=True, matrices=True, data_matrix=data1,
                        spaceAfter=50, spaceBefore=20, colWidths=colWidths)
            del data1['group']

            data = []

            if body['data']:
                for dnum in data1:
                    for da in data1[dnum]:
                        aux = []
                        aux.append(da)
                        aux.append(round(data1[dnum][da], 2))
                        data.append(aux)

                addTablePdf(proposals, elements, data, style5, sLeft, None, bold=False, boldPreguntas=False,
                            pos=False,
                            ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False, ap12=False,
                            ap15=False, ap16=False, ap17=False, ap18=False, italic=True, matrices=False,
                            data_matrix={}, spaceAfter=50, spaceBefore=20, colWidths=())

            data = []
            aux = []
            aux.append(gettext('Se eligen mutuamente'))
            aux.append(str(int(mutual / 2)))
            data.append(aux)

            addTablePdf(proposals, elements, data, style6, sLeft, None, bold=False, boldPreguntas=False,
                        pos=False,
                        ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False, ap12=False,
                        ap15=False, ap16=False, ap17=False, ap18=False, italic=False, matrices=False,
                        data_matrix={}, spaceAfter=50, spaceBefore=20, colWidths=())

            data = []
            aux = []
            s.fontSize = 10
            elements.append(Paragraph(gettext("Matriz pregunta tipo 2"), s))

            aux.append('#')
            colWidths = (10 * mm,)
            for al in alumnos:
                for a in alumnosInitials:
                    if alumnosInitials[a][1] == al[1]:
                        aux.append(a)
                        colWidths = colWidths + (None,)
            data.append(aux)
            aux = []
            aux.append("SN")
            for a in alumnos:
                for user in sn:
                    if user == a[1]:
                        aux.append(str(sn[user]))
            data.append(aux)
            if body['spv']:
                aux = []
                aux.append("SN val")
                for a in alumnos:
                    for user in snval:
                        if user == a[1]:
                            aux.append(str(snval[user]))
                data.append(aux)
            if body['np']:
                aux = []
                aux.append("NN")
                for a in alumnos:
                    for user in nn:
                        if user == a[1]:
                            aux.append(str(nn[user]) + "%")
                data.append(aux)


            data2['group'] = 2
            addTablePdf(proposals, elements, data, style4, sLeft, None, bold=False, boldPreguntas=False,
                        pos=False,
                        ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False, ap12=False,
                        ap15=False, ap16=False, ap17=False, ap18=False, italic=True, matrices=True,
                        data_matrix=data2, spaceAfter=50, spaceBefore=20, colWidths=colWidths)
            del data2['group']

            if body['data']:
                data = []
                for dnum in data2:
                    for da in data2[dnum]:
                        aux = []
                        aux.append(da)
                        aux.append(str(round(data2[dnum][da], 2)))
                        data.append(aux)


                addTablePdf(proposals, elements, data, style5, sLeft, None, bold=False, boldPreguntas=False,
                            pos=False,
                            ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False, ap12=False,
                            ap15=False, ap16=False, ap17=False, ap18=False, italic=True, matrices=False,
                            data_matrix={}, spaceAfter=50, spaceBefore=20, colWidths=())

            data = []
            aux = []
            aux.append(gettext('Se rechazan mutuamente'))
            aux.append(str(int(reject / 2)))
            data.append(aux)

            addTablePdf(proposals, elements, data, style7, sLeft, None, bold=False, boldPreguntas=False,
                        pos=False,
                        ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False, ap12=False,
                        ap15=False, ap16=False, ap17=False, ap18=False, italic=False, matrices=False,
                        data_matrix={}, spaceAfter=50, spaceBefore=20, colWidths=())

        if body['ep'] or body['rp']:
            data = []
            aux = []
            s.fontSize = 10
            elements.append(Paragraph(gettext("Matrices preguntas tipo 1 y 2"), s))

            aux.append('#')
            for t in titlematrix12:
                aux.append(titlematrix12[t])
            data.append(aux)
            aux = []
            for al in alumnos:
                for a in alumnosInitials:
                    if alumnosInitials[a][1] == al[1]:
                        for student in matrix12:
                            if student == alumnosInitials[a][1]:
                                aux.append(a)
                                for ti in titlematrix12:
                                    for value in matrix12[student]:
                                        if value == titlematrix12[ti]:
                                            if (value == "EP" or value == "EN") and body['ep']:
                                                aux.append(str(matrix12[student][value]) + "%")
                                            elif body['rp']:
                                                aux.append(str(matrix12[student][value]))
                                data.append(aux)
                                aux = []

            addTablePdf(proposals, elements, data, style3, sLeft, None, bold=False, boldPreguntas=False,
                        pos=False,
                        ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False, ap12=False,
                        ap15=False, ap16=False, ap17=False, ap18=False, italic=True, matrices=True,
                        data_matrix={}, spaceAfter=50, spaceBefore=20, colWidths=())

        if body['os']:
            data = []
            aux = []
            aux.append('OS')
            aux.append(str(os))
            data.append(aux)

            addTablePdf(proposals, elements, data, style8, sLeft, None, bold=False, boldPreguntas=False,
                        pos=False,
                        ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False, ap12=False,
                        ap15=False, ap16=False, ap17=False, ap18=False, italic=False, matrices=False,
                        data_matrix={}, spaceAfter=50, spaceBefore=20, colWidths=())

        if body['ic'] and body['iap']: #TODO SEPARAR O NO
            data = []
            aux = []
            s.fontSize = 10
            elements.append(Paragraph(gettext("Índices grupales"), s))

            if body['ic']:
                aux.append('Ic')
            if body['iap']:
                aux.append('Iap')
            data.append(aux)
            aux = []
            if body['ic']:
                ic = list(proposals['ic'].items())[0]
                aux.append(str(ic[0]) + "% - " + ic[1])
            if body['iap']:
                iap = list(proposals['iap'].items())[0]
                aux.append(str(iap[0]) + "% - " + iap[1])
            data.append(aux)

            addTablePdf(proposals, elements, data, style3, sLeft, None, bold=False, boldPreguntas=False,
                        pos=False,
                        ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False, ap12=False,
                        ap15=False, ap16=False, ap17=False, ap18=False, italic=False, matrices=True,
                        data_matrix={'c': [gettext('Bajo'), gettext('Muy bajo')]}, spaceAfter=0, spaceBefore=20,
                        colWidths=())

            data = []
            aux = []
            if body['ic']:
                aux.append('Id')
            if body['iap']:
                aux.append('Ian')
            data.append(aux)
            aux = []
            if body['ic']:
                id = list(proposals['id'].items())[0]
                aux.append(str(id[0]) + "% - " + id[1])
            if body['iap']:
                ian = list(proposals['ian'].items())[0]
                aux.append(str(ian[0]) + "% - " + ian[1])
            data.append(aux)

            addTablePdf(proposals, elements, data, style3, sLeft, None, bold=False, boldPreguntas=False,
                        pos=False,
                        ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False, ap12=False,
                        ap15=False, ap16=False, ap17=False, ap18=False, italic=False, matrices=True,
                        data_matrix={'c': [gettext('Alto'), gettext('Muy alto')]}, spaceAfter=50,
                        spaceBefore=20, colWidths=())

        if body['ip']:
            data = []
            aux = []
            s.fontSize = 10
            elements.append(Paragraph(gettext("Matriz pregunta tipo 3"), s))

            aux.append('#')
            colWidths = (9.75 * mm,)
            for al in alumnos:
                for a in alumnosInitials:
                    if alumnosInitials[a][1] == al[1]:
                        aux.append(a)
                        colWidths = colWidths + (None,)
            data.append(aux)
            aux = []
            aux.append("IP")
            for a in alumnos:
                for user in ip:
                    if user == a[1]:
                        aux.append(str(ip[user]))
            data.append(aux)

            if body['ipv']:
                aux = []
                aux.append("IP val")
                for a in alumnos:
                    for user in snval:
                        if user == a[1]:
                            aux.append(str(ipval[user]))
                data.append(aux)

            if body['imp']:
                aux = []
                aux.append("Imp")
                for a in alumnos:
                    for user in nn:
                        if user == a[1]:
                            aux.append(str(imp[user]) + "%")
                data.append(aux)

            data3['group'] = 3
            addTablePdf(proposals, elements, data, style4, sLeft, None, bold=False, boldPreguntas=False,
                        pos=False,
                        ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False,
                        ap12=False,
                        ap15=False, ap16=False, ap17=False, ap18=False, italic=True, matrices=True,
                        data_matrix=data3, spaceAfter=50, spaceBefore=20, colWidths=colWidths)
            del data3['group']

            if body['data']:
                data = []
                for dnum in data3:
                    for da in data3[dnum]:
                        aux = []
                        aux.append(da)
                        aux.append(str(round(data3[dnum][da], 2)))
                        data.append(aux)


                addTablePdf(proposals, elements, data, style5, sLeft, None, bold=False, boldPreguntas=False,
                            pos=False,
                            ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False,
                            ap12=False,
                            ap15=False, ap16=False, ap17=False, ap18=False, italic=True, matrices=False,
                            data_matrix={}, spaceAfter=50, spaceBefore=20, colWidths=())

            data = []
            aux = []
            s.fontSize = 10
            elements.append(Paragraph(gettext("Matriz pregunta tipo 4"), s))

            aux.append('#')
            colWidths = (9.75 * mm,)
            for al in alumnos:
                for a in alumnosInitials:
                    if alumnosInitials[a][1] == al[1]:
                        aux.append(a)
                        colWidths = colWidths + (None,)
            data.append(aux)
            aux = []
            aux.append("IN")
            for a in alumnos:
                for user in iN:
                    if user == a[1]:
                        aux.append(str(iN[user]))
            data.append(aux)
            if body['ipv']:
                aux = []
                aux.append("IN val")
                for a in alumnos:
                    for user in inval:
                        if user == a[1]:
                            aux.append(str(inval[user]))
                data.append(aux)
            if body['imp']:
                aux = []
                aux.append("Imn")
                for a in alumnos:
                    for user in imn:
                        if user == a[1]:
                            aux.append(str(imn[user]) + "%")
                data.append(aux)


            data4['group'] = 4
            addTablePdf(proposals, elements, data, style4, sLeft, None, bold=False, boldPreguntas=False,
                        pos=False,
                        ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False,
                        ap12=False,
                        ap15=False, ap16=False, ap17=False, ap18=False, italic=True, matrices=True,
                        data_matrix=data4, spaceAfter=50, spaceBefore=20, colWidths=colWidths)
            del data4['group']

            if body['data']:
                data = []
                for dnum in data4:
                    for da in data4[dnum]:
                        aux = []
                        aux.append(da)
                        aux.append(str(round(data4[dnum][da], 2)))
                        data.append(aux)

                addTablePdf(proposals, elements, data, style5, sLeft, None, bold=False, boldPreguntas=False,
                            pos=False,
                            ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False,
                            ap12=False,
                            ap15=False, ap16=False, ap17=False, ap18=False, italic=True, matrices=False,
                            data_matrix={}, spaceAfter=50, spaceBefore=20, colWidths=())

        if body['pp'] and body['pap']: #TODO SEPARAR O NO
            data = []
            aux = []

            aux.append('#')
            for t in titlematrix34:
                aux.append(titlematrix34[t])
            data.append(aux)
            aux = []
            for al in alumnos:
                for a in alumnosInitials:
                    if alumnosInitials[a][1] == al[1]:
                        for student in matrix34:
                            if student == alumnosInitials[a][1]:
                                aux.append(a)
                                for ti in titlematrix34:
                                    for value in matrix34[student]:
                                        if value == titlematrix34[ti]:
                                            if (value == "PP" or value == "PN") and body['pp']:
                                                aux.append(str(matrix34[student][value]) + "%")
                                            elif body['pap']:
                                                aux.append(str(matrix34[student][value]))
                                data.append(aux)
                                aux = []
            addTablePdf(proposals, elements, data, style3, sLeft, None, bold=False, boldPreguntas=False,
                        pos=False,
                        ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False,
                        ap12=False,
                        ap15=False, ap16=False, ap17=False, ap18=False, italic=True, matrices=True,
                        data_matrix={}, spaceAfter=50, spaceBefore=20, colWidths=())
        if body['oip']:
            data = []
            aux = []
            aux.append(gettext('Cree que lo eligen y acierta'))
            aux.append(str(believe))
            data.append(aux)
            aux = []
            aux.append('OIP')
            aux.append(str(oip))
            data.append(aux)
            aux = []
            aux.append(gettext('Cree que lo rechazan y acierta'))
            aux.append(str(believeNo))
            data.append(aux)
            aux = []
            aux.append('OIN')
            aux.append(str(oin))
            data.append(aux)

            addTablePdf(proposals, elements, data, style9, sLeft, None, bold=False, boldPreguntas=False,
                        pos=False,
                        ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False,
                        ap12=False,
                        ap15=False, ap16=False, ap17=False, ap18=False, italic=False, matrices=False,
                        data_matrix={}, spaceAfter=50, spaceBefore=20, colWidths=())
        if body['ipp']:
            data = []
            aux = []
            s.fontSize = 10
            elements.append(Paragraph(gettext("Matriz pregunta tipo 5"), s))

            aux.append('#')
            colWidths = (10 * mm,)
            for al in alumnos:
                for a in alumnosInitials:
                    if alumnosInitials[a][1] == al[1]:
                        aux.append(a)
                        colWidths = colWidths + (None,)
            data.append(aux)
            aux = []
            aux.append("IPP")
            for a in alumnos:
                for user in ipp:
                    if user == a[1]:
                        aux.append(str(ipp[user]) + "%")
            data.append(aux)

            addTablePdf(proposals, elements, data, style4, sLeft, None, bold=False, boldPreguntas=False,
                        pos=False,
                        ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False,
                        ap12=False,
                        ap15=False, ap16=False, ap17=False, ap18=False, italic=True, matrices=True,
                        data_matrix={'group': 5}, spaceAfter=50, spaceBefore=20, colWidths=colWidths)

            data = []
            aux = []
            s.fontSize = 10
            elements.append(Paragraph(gettext("Matriz pregunta tipo 6"), s))

            aux.append('#')
            colWidths = (10 * mm,)
            for al in alumnos:
                for a in alumnosInitials:
                    if alumnosInitials[a][1] == al[1]:
                        aux.append(a)
                        colWidths = colWidths + (None,)
            data.append(aux)
            aux = []
            aux.append("IPN")
            for a in alumnos:
                for user in ipn:
                    if user == a[1]:
                        aux.append(str(ipn[user]) + "%")
            data.append(aux)

            addTablePdf(proposals, elements, data, style4, sLeft, None, bold=False, boldPreguntas=False,
                        pos=False,
                        ap1=False, ap2=False, ap3=False, ap4=False, ap7=False, ap8=False, ap11=False,
                        ap12=False,
                        ap15=False, ap16=False, ap17=False, ap18=False, italic=True, matrices=True,
                        data_matrix={'group': 6}, spaceAfter=50, spaceBefore=20, colWidths=colWidths)

        elements.append(PageBreak())

        s.fontSize = 11
        elements.append(Paragraph(gettext("Propuesta de intervención grupal"), s))
        s.fontSize = 10
        elements.append(Paragraph(gettext("Áreas"), s))
        elements.append(Spacer(1, 0.1 * inch))
        d = Drawing(760, 1)
        d.add(Line(0, 0, 760, 0))
        elements.append(d)
        elements.append(Spacer(1, 0.25 * inch))

        sLeft.textColor = 'black'
        listProposals = []
        for vari in proposals['recomendaciones']:
            if ((vari == "IC" or vari == "ID") and not_empty(proposals['recomendaciones'][vari])):
                title = return_des(proposals['recomendaciones'][vari])
                listProposals.append(
                    ListItem(Paragraph(vari + ": " + title, sLeft),
                             spaceAfter=10))
                firstList = []
                for varinum in proposals['recomendaciones'][vari]:
                    for ex in proposals['recomendaciones'][vari][varinum]:
                        if (not_empty_ex(proposals['recomendaciones'][vari][varinum][ex])):
                            firstList.append(ListItem(Paragraph(ex, sLeft), spaceAfter=10))
                            secondList = []
                            for num in proposals['recomendaciones'][vari][varinum][ex]:
                                for secondArea in proposals['recomendaciones'][vari][varinum][ex][num]:
                                    if len(proposals['recomendaciones'][vari][varinum][ex][num][secondArea]):
                                        secondList.append(ListItem(Paragraph("<link href='" + return_link(proposals['recomendaciones'][vari][varinum][ex][num][secondArea]) + "' color='blue'><u>" + secondArea + "</u></link>", sLeft), spaceAfter=10))
                                        for studentProp in proposals['recomendaciones'][vari][varinum][ex][num][
                                            secondArea]:
                                            reasonsList = []
                                            for i, reasons in enumerate(
                                                    proposals['recomendaciones'][vari][varinum][ex][num][
                                                        secondArea][studentProp]):
                                                if i != 0 and reasons != title:
                                                    reasonsList.append(ListItem(Paragraph(reasons, sLeft)))
                                            secondList.append(ListItem(
                                                ListFlowable(reasonsList, bulletType='bullet', start='diamond',
                                                             leftIndent=10,
                                                             bulletFontSize=7, bulletOffsetY=-2),
                                                bulletColor="white", spaceAfter=15))
                            firstList.append(ListItem(
                                ListFlowable(secondList, bulletType='bullet', start='rarrowhead', leftIndent=10,
                                             bulletFontSize=7, bulletOffsetY=-2), bulletColor="white",
                                spaceAfter=15))
                listProposals.append(ListItem(
                    ListFlowable(firstList, bulletType='bullet', start='square', leftIndent=10,
                                 bulletFontSize=5,
                                 bulletOffsetY=-3), bulletColor="white", spaceAfter=20))
        t = ListFlowable(listProposals, bulletType='bullet', bulletOffsetY=2)

        elements.append(t)

        doc.multiBuild(elements, canvasmaker=FooterCanvas)
        pdfPrint = buffer.getvalue()
        buffer.close()
        response = make_response(pdfPrint)
        response.headers.set('Content-Disposition', 'attachment',
                             filename="Informe-Completo-Cuestionario-{0}.pdf".format(test.nombre))
        response.headers.set('Content-Type', 'application/pdf')
        db.session.close()
        return [response, fileNames]
    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)


def show_results_complete(request, pdf):
    try:
        body = request.get_json()
        user_id = get_jwt_identity()
        teacher = db.session.query(Profesor, User).join(User, and_(Profesor.user == user_id,
                                                                   Profesor.user == User.id, )).one()
        preferencias = Preferencias.query.filter(Preferencias.user == user_id).one().serialize
        body = {**body, **preferencias}
        test = Test.query.get(body['test'])
        preguntas = test.preguntas
        alumnos = db.session.query(Alumno, AlumnosTest.c.code, User.nombre, User.apellidos, AlumnosTest.c.answer, User.DNI, User.fecha_nacimiento, AlumnosClase.c.clase, AlumnosClase.c.alias).join(
            AlumnosTest,
            and_(
                test.id == AlumnosTest.c.test,
                AlumnosTest.c.alumno == Alumno.id, )) \
            .join(User, User.id == Alumno.user).join(AlumnosClase, and_(AlumnosClase.c.clase == test.clase, AlumnosClase.c.alumno == Alumno.id)).all()

        als = {}
        anyAnswer = False
        for a in alumnos:
            als[a[2] + " " + a[3]] = str(a[1])
            if a[4] == 1:
                anyAnswer = True
        if not anyAnswer:
            db.session.close()
            raise NotResults

        matrix = {}
        respuestasNum = {}
        createMatrix(test, preguntas, alumnos, matrix, "no", respuestasNum)

        # DECLARAR VARIABLES
        sp, spval, np, sn, snval, nn, ip, ipval, imp, iN, inval, imn, ipp, ipval5, ipn, inval6, matrix12, matrix34 = {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}

        # INICIALIZAR VARIABLES
        mutual, os, reject, believe, believeNo, oip, oin = processAnswersMatrix(body, matrix, matrix12, matrix34, sp,
                                                                                spval, sn, snval, ip, ipval, iN, inval,
                                                                                ipp,
                                                                                ipval5, ipn, inval6, respuestasNum,
                                                                                True)

        num_alumnos = len(alumnos)

        # if body['spv'] and body['np']:
        #     calculateNpNn(np, nn, spval, snval, num_alumnos)
        #
        # if body['ipv']:
        #     calculateImpImnIppIpn(imp, imn, ipp, ipn, ipval, inval, ipval5, inval6, num_alumnos, body['ipp'],
        #                           body['imp'])

        matrix12aux = copy.deepcopy(matrix12)
        matrix34aux = copy.deepcopy(matrix34)

        # if body['ic']:
        #     ic, id = calculateGroupVariables(matrix12)
        #     ic = int((float(ic) / ((num_alumnos - 1) * MAX_POINTS)) * 100)
        #     id = int((float(id) / ((num_alumnos - 1) * MAX_POINTS)) * 100)

        # if body['pap']:
        #     calculatePapPanPpPn(matrix34, body['pp'])

        # if body['iap']:
        #     iap = int((float(sum(sp.values())) / (MAX_POINTS * num_alumnos)) * 100)
        #     ian = int((float(sum(sn.values())) / (MAX_POINTS * num_alumnos)) * 100)

        data1, data2, data3, data4 = {}, {}, {}, {}

        # CALCULAR LAS TABLAS DE DATOS
        calculateDataSP(data1, data2, sp, num_alumnos, sn)
        calculateDataIP(data3, data4, ip, num_alumnos, iN)

        clase = Clase.query.get(test.clase)

        matrixaux = {}

        for ma in respuestasNum:
            matrixaux[ma] = {}
            for re in respuestasNum[ma]:
                for al in respuestasNum[ma][re]:
                    matrixaux[ma][al] = {}
                    for res in respuestasNum[ma][re][al]:
                        matrixaux[ma][al][res] = respuestasNum[ma][re][al][res]

        proposals = get_proposals(sp, np, nn, sn, spval, snval, imp, ipval, imn, inval, iN, ip, ipp, ipval5, ipn,
                                  inval6, data1, data2, data3, data4, num_alumnos, matrix12aux, matrix34aux, matrixaux,
                                  '', {},
                                  clase.grupo_edad, body)

        titlematrix12 = {1: "EP", 2: "RP", 3: "EN", 4: "RN"}
        titlematrix34 = {1: "PP", 2: "PAP", 3: "PN", 4: "PAN"}

        # icValue = escala(0, proposals['ic'])
        # idValue = escala(1, proposals['id'])
        # iapValue = escala(0, proposals['iap'])
        # ianValue = escala(1, proposals['ian'])

        alumnosInitials = {}
        aux = {}  # TODO REVISAR DIMINUTIVO
        for al in alumnos:
            name = " ".join(al[2].split()).strip()
            surname = " ".join(al[3].split()).strip()
            if " " not in surname.strip():
                if name[0] + surname[0] not in aux:
                    alumnosInitials[name[0] + surname[0]] = al
                    aux[name[0] + surname[0]] = 1
                else:
                    aux[name[0] + surname[0]] += 1
                    alumnosInitials[name[0] + surname[0] + str(
                        aux[name[0] + surname[0]])] = al
            else:
                if name[0] + surname.split(" ")[0][0] + surname.split(" ")[1][0] not in aux:
                    alumnosInitials[
                        name[0] + surname.split(" ")[0][0] + surname.split(" ")[1][0]] = al
                    aux[name[0] + surname.split(" ")[0][0] + surname.split(" ")[1][0]] = 1
                else:
                    aux[name[0] + surname.split(" ")[0][0] + surname.split(" ")[1][0]] += 1
                    alumnosInitials[
                        name[0] + surname.split(" ")[0][0] + surname.split(" ")[1][0] + str(aux[name[0] +
                                                                                             surname.split(" ")[0][0] +
                                                                                             surname.split(" ")[1][
                                                                                                 0]])] = al

        clase = Clase.query.get(test.clase)

        if pdf == 1:
            return producePdfComplete(test, matrixaux, respuestasNum, teacher, clase, sp, sn, matrix12,
                                      matrix34,
                                      proposals, np, nn, os, oip, oin, ip, iN, ipp, ipn, imp, imn, body, alumnos,
                                      alumnosInitials, als, data1, data2, data3, data4, spval,
                                      snval, ipval, inval, titlematrix12, titlematrix34, mutual, reject, believe,
                                      believeNo)
        else:
            db.session.close()
            return jsonify(
                {'test': test.serialize, 'clase': clase.nombre, 'preguntas': [i.serialize for i in preguntas],
                 'alumnos':
                     [{**al[0].serialize(al[7], al[1]), 'nombre': " ".join(al[2].split()).strip(),
                       'apellidos': " ".join(al[3].split()).strip(), 'answer': al[4], 'DNI': al[5], 'fecha_nacimiento': al[6], 'alias': al[8]} for al in
                      alumnos],
                 'spValue': data1[8]['Xinf'], 'snValue': data2[7]['Xsup'], 'ipValue': data3[8]['Xinf'],
                 'inValue': data4[7]['Xsup'],
                 'respuestasNum': respuestasNum, 'mutual': int(mutual / 2), 'os': os,
                 'reject': int(reject / 2), 'believe': believe, 'believeNo': believeNo, 'oip': oip,
                 'oin': oin,
                 'sp': sp, 'spval': spval, 'np': np, 'data1': data1, 'sn': sn, 'snval': snval, 'nn': nn,
                 'data2': data2, 'matrix12': matrix12, "title_matrix12": titlematrix12,
                 'ic': proposals['ic'], 'id': proposals['id'], 'iap': proposals['iap'], 'ian': proposals['ian'], 'ip': ip, 'ipval': ipval, 'imp': imp,
                 'data3': data3, 'in': iN, 'inval': inval, 'imn': imn, 'data4': data4,
                 'matrix34': matrix34, 'title_matrix34': titlematrix34, 'ipp': ipp, 'ipn': ipn,
                 'teacher': {**teacher[0].serialize, **teacher[1].serialize}, 'testName': test.nombre,
                 'date': test.date_created.strftime('%d/%m/%Y %H:%M'),
                 'initials': [{al:alumnosInitials[al][1]} for al in alumnosInitials]})

    except NotResults:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
        raise NotResults
    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)


class ResultadosCompletosApi(Resource):
    @profesor
    def post(self):
        try:
            db.openSession()
            return show_results_complete(request, pdf=False)
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

class CheckAnswersApi(Resource):
    @profesor
    def get(self, id):
        try:
            db.openSession()
            alumnos = db.session.query(Alumno, AlumnosTest.c.code).join(
                AlumnosTest,
                and_(
                    int(id) == AlumnosTest.c.test,
                    AlumnosTest.c.alumno == Alumno.id, )).count()
            print(alumnos)
            if alumnos == 0:
                raise NotResults
            else:
                return "Hay resultados", 200
        except NotResults:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise NotResults
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError


class ResultadosCompletosPdfApi(Resource):
    @profesor
    def post(self):
        try:
            db.openSession()
            res = show_results_complete(request, pdf=True)
            for f in res[1]:
                osL.remove(f)
            return res[0]
        except NotResults:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise NotResults
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError


class ResultadosStudentApi(Resource):
    @profesor
    def post(self):
        try:
            db.openSession()
            return show_results_student(request, pdf=False, all=False)
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError


class ResultadosStudentPdfApi(Resource):
    @profesor
    def post(self):
        try:
            db.openSession()
            return show_results_student(request, pdf=True, all=False)
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError


class ResultadosAllStudentsApi(Resource):
    @profesor
    def post(self):
        try:
            db.openSession()
            body = request.get_json()
            test = Test.query.get(body['test'])
            alumnos = db.session.query(Alumno, AlumnosTest.c.code, User.nombre, User.apellidos).join(AlumnosTest,
                                                                  and_(
                                                                      test.id == AlumnosTest.c.test,
                                                                      AlumnosTest.c.alumno == Alumno.id, AlumnosTest.c.answer == 1)) \
                .join(User, User.id == Alumno.user).all()

            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=100, bottomMargin=50)
            doc.pagesize = portrait(A4)
            elements = []
            if alumnos:
                for alumno in alumnos:
                    elements.extend(show_results_student(request, pdf=True, all=True, alumno=alumno[1]))
                    elements.append(PageBreak())
                doc.multiBuild(elements, canvasmaker=FooterCanvas)
                pdfPrint = buffer.getvalue()
                buffer.close()
                response = make_response(pdfPrint)
                response.headers.set('Content-Disposition', 'attachment',
                                     filename="Informes-Individuales-Cuestionario-{0}.pdf".format(
                                         test.nombre))
                response.headers.set('Content-Type', 'application/pdf')
                db.session.close()
                return response
            else:
                db.session.close()
                raise NotResults
        except NotResults:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise NotResults
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError


class ResultadosApi(Resource):
    @profesor
    def post(self):
        try:
            db.openSession()
            body = request.get_json()
            print(body['idioma'])
            user_id = get_jwt_identity()
            teacher = db.session.query(Profesor, User).join(User, and_(Profesor.user == user_id,
                                                                       Profesor.user == User.id, )).one()
            preferencias = Preferencias.query.filter(Preferencias.user == user_id).one().serialize
            body = {**body, **preferencias}
            test = Test.query.get(body['test'])
            preguntas = test.preguntas
            alumnos = db.session.query(Alumno, AlumnosTest.c.code, User.nombre, User.apellidos, AlumnosTest.c.answer, User.DNI, User.fecha_nacimiento, AlumnosClase.c.clase, AlumnosClase.c.alias).join(AlumnosTest,
                                                                                                     and_(
                                                                                                         test.id == AlumnosTest.c.test,
                                                                                                         AlumnosTest.c.alumno == Alumno.id, )) \
                .join(User, User.id == Alumno.user).join(AlumnosClase, and_(AlumnosClase.c.clase == test.clase, AlumnosClase.c.alumno == Alumno.id)).all()
            als = {}
            for a in alumnos:
                als[a[2] + " " + a[3]] = str(a[1])

            matrix = {}
            createMatrix(test, preguntas, alumnos, matrix, 'no', "no")

            # DECLARAR VARIABLES
            sp, spval, np, sn, snval, nn, ip, ipval, imp, iN, inval, imn, ipp, ipval5, ipn, inval6, matrix12, matrix34 = {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}

            # INICIALIZAR VARIABLES
            processAnswersMatrix(body, matrix, matrix12, matrix34, sp, spval, sn, snval, ip, ipval, iN, inval, ipp,
                                 ipval5, ipn, inval6, "no", False)

            num_alumnos = len(alumnos)
            data1, data2, data3, data4 = {}, {}, {}, {}

            # CALCULAR LAS TABLAS DE DATOS
            calculateDataSP(data1, data2, sp, num_alumnos, sn)
            calculateDataIP(data3, data4, ip, num_alumnos, iN)

            clase = Clase.query.get(test.clase)

            # OBTENER RECOMENDACIONES
            proposals = get_proposals(sp, np, nn, sn, spval, snval, imp, ipval, imn, inval, iN, ip, ipp, ipval5, ipn,
                                      inval6, data1, data2, data3, data4, num_alumnos, matrix12, matrix34, matrix, '',
                                      {},
                                      clase.grupo_edad, body)
            db.session.close()
            return jsonify({'eva': teacher[0].evaluacion, 'clase': clase.nombre,
                            'preguntas': [i.serialize for i in preguntas],
                            'respuestas': json.dumps(matrix), 'ic': proposals['ic'], 'id': proposals['id'],
                            'iap': proposals['iap'], 'ian': proposals['ian'], 'alumnos': json.dumps(als),
                            'sp': json.dumps(sp), 'sn': json.dumps(sn),
                            'ip': json.dumps(ip), 'iN': json.dumps(iN), 'recomendaciones': proposals['recomendaciones'],
                            'alumnosQuery': [{**i[0].serialize(i[7], i[1]), 'nombre': i[2], 'apellidos': i[3], 'answer': i[4], 'DNI': i[5], 'fecha_nacimiento': i[6], 'alias': i[8]} for i in alumnos]})
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb.tb_lineno, flush=True)
            raise InternalServerError

