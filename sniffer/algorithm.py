import sqlite3 as sql
import os, sys
import difflib
import logging

def formatText(txt, lang) :
    # We remove all the whitespace and newline characters. They are meaningless
    # for algorithm.
    txt = ' '.join( txt.split() )
    if lang == "vhdl" :
        import lang_vhdl as vhdl
        obj = vhdl.VHDL()
        return obj.fix_text(txt)
    if lang == "verilog" :
        import lang_verilog as verilog
        obj = verilog.Verilog()
        return obj.fix_text(txt)
    if lang == "pdf" :
        import lang_pdf as pdf
        # NOTE: txt is filename
        obj = pdf.Pdf()
        return obj.fix_text(txt)
    if lang == "text":
        return txt
    else :
        logging.warn("This language is not supported. Assuming text ...")
        return txt

def compareAndReturnResult(textA, textB, algorithm="subsequence" ) :
    wordsA = textA.split()
    wordsB = textB.split()

    if len(wordsA) < 4 or len(wordsB) < 4 :
        return "Less than four words", 0.0

    lR = float(len(wordsA)) / len(wordsB)
    if lR > 1.0 :
        lR = 1/lR
    if lR < 0.1 :
        return "One file is order of magnitude larger than the other", lR

    # check intersection of keywords
    setA = set(wordsA)
    setB = set(wordsB)

    # if intersection of these two set is very small then there is little
    # maching in these two files.
    intersectionSize =  float(len(setA.intersection(setB))) / min(len(setA), len(setB))
    if intersectionSize < 0.25 :
        return "Small keyword intersection", intersectionSize

    # When intersection size is bigger than difflib ration, return the
    # intersection size.
    logging.debug("Computing matching using difflib")
    s = difflib.SequenceMatcher(None, textA, textB)
    return "difflib", max( s.ratio(), intersectionSize )


def commonPrefix(string1, string2) :
    prefix = ""
    done = False;
    i = 0
    while(done == False) :
        if string1[i] == string2[i] :
            prefix += string1[i]
        else :
            done = True
        i += 1
    return prefix
