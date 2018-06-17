import Semantics as S
import re as re

class BasicBlock:
    """les BasicBlocks sont des instruction sans sauts, 
        self.start est le numéro de leur première ligne
        self.end est le numéro de leur dernière ligne (saut compris)
        self.code est la liste des lignes de code qu'ils contiennent
    """

    def __init__(self,_lines,m_start,m_end):
        
        self.start = m_start
        self.end = m_end
        self.code = _lines[m_start:m_end]

    def __str__(self):

        return "start: %d, end: %d"%(self.start,self.end)

global nones
nones = "," #nom de variable impossible qui représente les lignes qui ne modifient pas de variables sans les effacer
class AsmCodeLine:
    """classe contenant les infos d'une ligne de code asm parsée
        self.modifiedVar est la variable modifiée par l'instruction, il n'y en a qu'une
        self.necessaryVars est la liste des variables utilisées pour modifiées self.modifiedVar
        self.instruction est un tag
        self.lineNumber est le numéro d ela ligne à laquelle correspond l'instruction
    """

    def __init__(self,line,m_lineNumber):
        global nones

        self.modifiedVar = nones
        self.necessaryVars = []
        self.instruction = None
        self.lineNumber = m_lineNumber

        if(line[0:4] == "mov "):

            self.instruction = line[0:3]
            
            firstElement = line[4:line.find(",")].replace(" ","")   #élement à gauche de la virgule
            if(firstElement[0] == "[" and firstElement[-1] == "]"): 
                self.modifiedVar = firstElement   
                self.necessaryVars.append(firstElement[1:len(firstElement)-1]) #si on accède a la valeur via [], dépend aussi de lui même
            else: 
                self.modifiedVar = firstElement 

            self.necessaryVars.append(line[line.find(",")+1:len(line)].replace(" ","")) #bien sur dépend aussi de l'élement de droite
        
        elif(line[0:4] == "add " or line[0:4] == "sub " or line[0:4] == "xor "):

            self.instruction = line[0:3]
            firstElement = line[4:line.find(",")].replace(" ","")
            self.modifiedVar = firstElement
            self.necessaryVars.append(self.modifiedVar)                                     #ces instructions dépendent des deux variables 
            self.necessaryVars.append(line[line.find(",")+1:len(line)].replace(" ",""))     #à droite et à gauche de la virgule
            
        elif(line[0:4] == "inc "):

            self.instruction = line[0:3]
            self.modifiedVar = line[4:line.find(",")].replace(" ","")
            self.necessaryVars.append(line[4:line.find(",")].replace(" ",""))   #pour l'incrémentation la variable ne dépend que d'elle même

        #push et pop sont traités en amont et interprétes comme une suite de deux instructions :
        # push <=> sub rsp, size(var) ; mov [rsp], var
        # pop  <=> mov var, [rsp] ; add rsp, size(var)

        elif(line[0:6] == "1push "):    #sub rsp, size(var)
            self.instruction = "1push"
            self.modifiedVar = "rsp"
            self.necessaryVars.append(line[6:].replace(" ",""))
            self.necessaryVars.append("rsp")
        elif(line[0:6]=="2push "):      #mov [rsp], var
            self.instruction = "2push"
            self.modifiedVar = "[rsp]"
            self.necessaryVars.append("rsp")
            self.necessaryVars.append(line[6:].replace(" ",""))

        elif(line[0:5] == "1pop "):     #mov var, [rsp]
            self.instruction = "1pop"
            self.modifiedVar = line[5:].replace(" ","")
            self.necessaryVars.append("[rsp]")
            self.necessaryVars.append("rsp")
            self.necessaryVars.append(line[5:].replace(" ","")) #commentez cette ligne pour optimisation meilleure (mais pas sur que ce soit correct)
        elif(line[0:5] == "2pop "):     #add rsp, size(var)
            self.instruction = "2pop"
            self.modifiedVar = "rsp"
            self.necessaryVars.append(line[5:].replace(" ","")) #commentez cette ligne pour optimisation meilleure (mais pas sur que ce soit correct)
            self.necessaryVars.append("rsp")
            
        else:#tout les cas imprévus on les garde de manbière solitaire pour ne pas les effacer
            nones +=","
            self.instruction = line[0:3]
            self.modifiedVar = nones

        #pour toutes les variables si on a quelque chose de la forme rax+8 ou rax-8 on crée une dépendance à rax et à 8
        if(self.modifiedVar.find("+")!=-1):
            self.modifiedVar = self.modifiedVar.replace(" ","")
            self.necessaryVars.append(self.modifiedVar.split("+")[0])
            self.necessaryVars.append(self.modifiedVar.split("+")[1])
        elif(self.modifiedVar.find("-")!=-1):
            self.modifiedVar = self.modifiedVar.replace(" ","")
            self.necessaryVars.append(self.modifiedVar.split("+")[0])
            self.necessaryVars.append(self.modifiedVar.split("+")[1])


global tabs
tabs = "" #tabs permet un print joli
class DependancyNode:
    """Noeud du graphe de dépendances
        self.parents est la liste des noeuds dont le noeud dépend
        self.lineNumber est le numéro de ligne associé au noeud
        self.name est le nom de la variable concernée par le noeud
    """

    def __init__(self,m_name,m_line):
        self.parents=[]
        self.lineNumber = m_line
        self.name = m_name

    def __str__(self):
        global tabs
        s = "V: %s ln:%d parents : "%(self.name,self.lineNumber)
        tabs+="    "
        for elt in self.parents:
            s+="\n"+tabs+str(elt)
        tabs= tabs[0:len(tabs)-4]
        return s

class DependancyGraph:
    """graphe des dépendances utilisé pour optimiser le code d'un BasicBlock
        self.bb est le basicblock à optimiser
        self.vars   est un dictionnaire qui recense les variables modifiées dans ce bloc, 
                    clés de type string et valeur de type DependancyNode
    """
    def __init__(self,block):
        
        self.bb = block
        self.vars = {}#dictionnaire nom-objet

    def __str__(self):
        s=""
        for v in self.vars:
            s+=str(self.vars[v])+"\n"
        return s

    def GenerateGraph(self):
        """génère le graphe de dépendances associé à self.bb"""

        code = self.ArrangeLines()#retourne une liste de AsmCodeLines 

        i=0
        while(i < len(code)):#pour chaque ligne de code on met à jour le graphe représenté par le dictionnaire "vars"

            x = DependancyNode(code[i].modifiedVar,code[i].lineNumber)#on crée la variable correspondante à l'AsmCodeLine numéro i
  
            #reste ensuite à lier la variable à ses parents
            for parent in code[i].necessaryVars:
                if(parent in self.vars):#s'ils existent déja on fait juste une liaison
                    x.parents.append(self.vars[parent])
                else:#sinon on crée un nouveau parent et on l'ajoute
                    p = DependancyNode(parent,code[i].lineNumber)
                    x.parents.append(p)

            self.vars[code[i].modifiedVar]=x #on ajoute/met à jour la variable dans le dictionnaire
            
            i +=1 

    def ArrangeLines(self):
        """Cette fonction transforme les lignes de code en AsmCodeLines plus faciles à utiliser"""

        asmCodeLines = []
        currentLine = 0 

        for line in self.bb.code:
            if(line[0:4]=="pop " or line[0:5]=="push "):#push et pop sont traitées comme deux instructions en une
                asmCodeLines.append(AsmCodeLine("1"+line,currentLine))
                asmCodeLines.append(AsmCodeLine("2"+line,currentLine))
            else:
                asmCodeLines.append(AsmCodeLine(line,currentLine))

            currentLine+=1

        return asmCodeLines

    def Optimize(self):
        """ Cette fonction retourne la liste des lignes de codes utiles pour le basicblock dans l'ordre"""

        usefulLines = set()#usefulLines contiendra les numéros des lignes de code à conserver

        for var in self.vars: #pour chaque variable modifiée

            debug = set()#debug donne juste un joli print de ce qui se passe
            debug.add((var,self.vars[var].lineNumber))

            usefulLines.add(self.vars[var].lineNumber)
            self.FindUsefulLines(self.vars[var],usefulLines,debug)
            #print(self.vars[var])
            #print(debug)
        
            
        newBlock = [] #newBlock est la liste des lignes de codes utiles

        for i in range(len(self.bb.code)):
            if(i in usefulLines):
                newBlock.append(self.bb.code[i])
        
        return newBlock


    def FindUsefulLines(self,var,usefulLines,debug):
        """Fonction recursives permettant de remonter l'arbre et de sotcker dans usefulLines toutes les lignes utiles
        pour la variable var
            -var est de type DependancyNode
            -usefulLines est la liste des lignes utiles
            -debug ne sert à rien mais est utile pour afficher ce qui se passe"""

        for parent in var.parents:
            debug.add((parent.name,parent.lineNumber))
            usefulLines.add(parent.lineNumber)
            self.FindUsefulLines(parent,usefulLines,debug)

class ControlFlowGraph:
    """Graphe qui une fois genérer contient tout les BasicBlocks du code asm associé
        self.firstLine  est actualisé lors de la lecture du fichier 
                        et permet de commencer l'analyse du code à la ligne section.text
        self.blocks est la liste des basicblocks qui composent le code
        self.lines est la liste des lignes du code
    """

    def __init__(self):
        self.firstLine =0
        self.blocks = []
        self.lines = []
    
    def __str__(self):
        string =""
        for b in self.blocks:
            string+=str(b)+","
        string+="\n"
        return string

    def ReadFile(self,asmFileName):
        """génère la liste des lignes du fichier désigné par asmFileName et la stocke dans self.lines"""
        asmFile = open(asmFileName,"r")
        textAsm = asmFile.readlines()

        for i in range(len(textAsm)):
            textAsm[i]=textAsm[i].rstrip('\n')

        self.lines = textAsm

    def FindEnds(self):
        """retourne la liste des numéros de lignes des fins de block"""
        jumps = {"jmp ","je ","jz ","jne ","jnz ","jg ","jnle ","jge ","jnl ","call ","ret"}#liste des tokens de sortie

        ends = []

        start=0
        while(self.lines[start]!="section .text"):
            start+=1
            if(start==len(self.lines)):
                return None

        for lineNumber in range(start,len(self.lines)):
            for jumpToken in jumps:
                if( jumpToken == self.lines[lineNumber][0:len(jumpToken)] ):
                    ends.append(lineNumber+1)
                    break
        
        self.firstLine = start+1
        return ends

    def BuildBlocks(self):
        """construit la liste blocks du graphe, ne les relient pas entre eux"""
        ends = self.FindEnds()
        if(ends==None):
           return

        self.blocks.append(BasicBlock(self.lines,self.firstLine,ends[0]))

        for i in range(1,len(ends)):
            self.blocks.append(BasicBlock(self.lines,ends[i-1],ends[i]))

    def ConnectBlocks(self):
        """connecte les blocks entre eux, pas nécessaire pour le moment"""
        pass

    def GenerateFrom(self,asmFileName):
        """crée le graphe à partir d'un fichier asm"""
        self.ReadFile(asmFileName)
        self.BuildBlocks()
        self.ConnectBlocks()
        # les trucs du types etiquette:, call

    def Optimize(self):
        """optimise le code du graphe"""

        #pour chaque bloc on fait le graphe des dépendances et on l'optimise
        for i in range(len(self.blocks)):
            a = DependancyGraph(self.blocks[i])
            a.GenerateGraph()
            self.blocks[i].code = a.Optimize()
        
        optimizedCode = []

        for j in range(len(self.blocks)):
            optimizedCode += self.blocks[j].code

        #on remet à jour le graphe avec le nouveau code
        self.lines = optimizedCode
        self.OptimizeMathIdentities()
        self.BuildBlocks()
        self.ConnectBlocks()
    
    def WriteCode(self):
        """retourne une chaine contenant le code associé au graphe"""
        code = ""
        for line in self.lines:
            code+=line+"\n"

        return code

    def OptimizeMathIdentities(self):
        """enleve les instruction du type a=a+0 ou a=a-0"""
        addIdentity = re.compile("add [\w]*, 0")
        subIdentity = re.compile("sub [\w]*, 0")
        
        i=0
        while i<len(self.lines):
            
            if(addIdentity.match(self.lines[i])!=None or subIdentity.match(self.lines[i])!=None):
                del(self.lines[i])
            else:
                i+=1

if __name__=="__main__":
    
    a = ControlFlowGraph()
    a.GenerateFrom("test.asm")
    a.Optimize()
    c = a.WriteCode()
    
    print(c)

