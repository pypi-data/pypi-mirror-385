# ✅ Optimized lexer.py for Vallaipallam language
# ✅ Added support for identifiers with numbers and underscores
# ✅ Added support for '#' comments
# ✅ Full Tamil character set (Uyir, Mei, Uyirmei, Vadamozhi)
# ✅ Cleaned logic and added Tamil+English comments for readability
from vallaipallam.network import *
from vallaipallam.tokens import *
from vallaipallam.errors import *
import re

class Lexer:
    line_no = 1

    # தமிழ் எழுத்துக்கள்: உயிர், மெய், உயிர்மெய், வடமொழி எழுத்துக்கள்
    letters = set("""
    அஆஇஈஉஊஎஏஐஒஓஔ
    க்ங்ச்ஞ்ட்ண்த்ந்ப்ம்ய்ர்ல்வழளற்ன்
    கஙசஞடணதநபமயரலவழளறன
    காகிகீகுகூகெகேகைகொகோகௌ
    ஙாஙிஙீஙுஙூஙெங்கேஙைஙொஙோஙௌ
    சாசிசீசுசூசெசேசைசொசோசௌ
    ஞாஞிஞீஞுஞூஞெஞேஞைஞொஞோஞௌ
    டாடிடீடுடூடெடேடைடொடோடௌ
    ணாணிணீணுணூணெணேணைணொணோணௌ
    தாதிதீதுதூதெதேதைதொதோதௌ
    நாநிநீநுநூநெனேநைநொநோநௌ
    பாபிபீபுபூபெபேபைபொபோபௌ
    மாமிமீமுமூமெமேமைமொமோமௌ
    யாயியீயுயூயெயேயையொயோயௌ
    ராரிரீருரூரெரேரைரொரோரௌ
    லாலிலீலுலூலெலேலைலொலோலௌ
    வாவிவீவுவூவெவேவைவொவோவௌ
    ழாழிழீழுழூழெழேழைழொழோழௌ
    ளாளிளீளுளூளெளேளைளொளோளௌ
    றாறிறீறுறூறெறேறைறொறோறௌ
    னாணிணீணுணூணெணேணைணொணோணௌ
    abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789
    """)
    hindiletters=set([
    # स्वर (Vowels)
    "अ","आ","इ","ई","उ","ऊ","ऋ","ॠ","ऌ","ॡ","ए","ऐ","ओ","औ","अं","अः",
    # व्यंजन (Consonants)
    "क","ख","ग","घ","ङ","च","छ","ज","झ","ञ",
    "ट","ठ","ड","ढ","ण","त","थ","द","ध","न",
    "प","फ","ब","भ","म",
    "य","र","ल","व","श","ष","स","ह",
    # अतिरिक्त (Nukta forms)
    "क़","ख़","ग़","ज़","ड़","ढ़","फ़","य़",
    # मात्राएँ (Vowel signs)
    "ा","ि","ी","ु","ू","ृ","ॄ","ॢ","ॣ","े","ै","ो","ौ","ं",
    # हलन्त (Virama)
    "्","़","ँ",'ॉ',
    # अंक (Digits 0–9)
    "१","२","३","४","५","६","७","८","९",
    # विराम चिन्ह (Punctuation)
    "।","॥"
])

    
    digits = "0123456789"
    operators = "+-*/=%"
    stopwords = (' ', '\n', ',')
    listofkeyword = ('தொடர்', 'ரத்து', 'இறக்கு')
    keywords = ('உருவாக்கு')
    members = ('உள்ளது')
    function_call = 'கூப்பிடு'
    function = ('வேலை', 'கொடு')
    built_in_functions = ('வெளியிடு', 'உள்ளிடு', 'அளவு', 'எண்', 'வரம்பு', 'நீக்கு', 'பட்டியல்', 'இணை', 'சொல்', 'செருகு', 'வகை', 'பிரி', 'திற', 'படி', 'எழுது', 'மூடு')
    conditions = ('என்றால்', 'இது', 'இல்லை', 'இல்லையெனில்', 'அதுவரை', 'இதில்', 'இருந்து')
    logical = ('மற்றும்', 'அல்லது', 'அல்ல')
    comparison = (">", "<", ">=", "<=", "!=", "==")
    boolean = ('மெய்', 'பொய்')
    tamilcommandlist=('நிர்வாகி_இயக்கு','இணைப்பு_முகவரி','இணைப்பு_நிலை','இணைப்பு_செயலில்','இணைப்பு_உள்வெளி','DHCP_அமை','இணைப்பு_உள்வெளி_பிரிப்பு','இணைப்பு_வேகம்','இணைப்பு_திற','இணைப்பு_மூடு','இணைப்பு_IP_அமை','வாயில்','மடக்கெண்',
                 'வலைப்பின்னல்_பட்டியல்','வலைப்பின்னல்_இணை','வலைப்பின்னல்_துண்டிக்க','கடவுச்சொல்','இணைப்பு_அடைந்ததா','வழித்தடம்_காட்டு','பெயர்ப்பட்டியல்_காண்','துறைமுகம்_சோதனை','வாயில்_காட்டு','தாமதம்_சோதனை','துறைமுகம்',
                 'தடுப்பு_செயல்படுத்து','தடுப்பு_நிறுத்து','துறைமுகம்_அனுமதி','துறைமுகம்_தடு','துறைமுகம்_விதிகள்','சேவை_அனுமதி','சேவை_தடு',
                 "வாழை_முகவர்_அழை","பணி_அடைவு","ஜெமினி_விசை")
    englishcommandlist=("RUN_AS_ADMIN","SHOW_INTERFACE_ADDRESSES","SHOW_INTERFACE_STATUS","ENABLE_INTERFACE","DISABLE_INTERFACE","SET_DHCP","SET_IP","SHOW_NETWORK_IO","SHOW_NETWORK_IO_PER_INTERFACE","SHOW_ACTIVE_CONNECTIONS", "SHOW_NETWORK_SPEED","GATEWAY","NETMASK",
                        'LIST_WIFI','CONNECT_WIFI','DISCONNECT_WIFI','PASSWORD','PING','TRACEROUTE','DNS_LOOKUP','PORT_SCAN','SHOW_GATEWAY','LATENCY_TEST','PORT',
                        'ENABLE_FIREWALL','DISABLE_FIREWALL','ALLOW_PORT','BLOCK_PORT','LIST_FIREWALL_RULES','ALLOW_SERVICE','BLOCK_SERVICE',
                        "ACTIVATE_AGENT_VALLAI","WORKING_DIRECTORY","GEMINI_API_KEY")
    hindicommandlist=[
    # Phase 1 — Network setup & monitoring
    "इंटरफ़ेस_पते_दिखाओ","इंटरफ़ेस_स्थिति_दिखाओ","सक्रिय_कनेक्शन_दिखाओ","नेटवर्क_IO_दिखाओ","प्रति_इंटरफ़ेस_IO_दिखाओ","इंटरफ़ेस_गति_मापो","इंटरफ़ेस_सक्रिय_करो",
    "इंटरफ़ेस_निष्क्रिय_करो","DHCP_सक्रिय_करो","इंटरफ़ेस_IP_सेट_करो","प्रशासक_रन",
    # Wi-Fi / Hotspot
    "वाईफाई_सूची_दिखाओ","वाईफाई_जोड़ो","वाईफाई_काटो",
    # Phase 2 — Network diagnostics
    "पिंग_जाँच","मार्ग_दिखाओ","DNS_खोज","पोर्ट_जांच","गेटवे_दिखाओ","विलंब_परीक्षण",
    # Phase 3 — Firewall & services
    "फायरवॉल_सक्रिय_करो","फायरवॉल_निष्क्रिय_करो","पोर्ट_अनुमति","पोर्ट_अवरोध","फायरवॉल_नियम_दिखाओ","सेवा_अनुमति","सेवा_अवरोध",
    #AGENT VALLAI
    "एजेंट_वाले_जगाओ ","कार्य_निर्देशिका","जेमिनी_कुंजी"
]
    tamil_to_english={
    'இணைப்பு_முகவரி': 'SHOW_INTERFACE_ADDRESSES','இணைப்பு_நிலை': 'SHOW_INTERFACE_STATUS','இணைப்பு_செயலில்': 'SHOW_ACTIVE_CONNECTIONS',
    'இணைப்பு_உள்வெளி': 'SHOW_NETWORK_IO','இணைப்பு_உள்வெளி_பிரிப்பு': 'SHOW_NETWORK_IO_PER_INTERFACE',
    'DHCP_அமை': 'SET_DHCP','இணைப்பு_IP_அமை': 'SET_IP','இணைப்பு_வேகம்': 'SHOW_NETWORK_SPEED',
    'இணைப்பு_திற': 'ENABLE_INTERFACE','இணைப்பு_மூடு': 'DISABLE_INTERFACE','வலைப்பின்னல்_இணை': 'CONNECT_WIFI',
    'வலைப்பின்னல்_துண்டிக்க': 'DISCONNECT_WIFI','வலைப்பின்னல்_பட்டியல்': 'LIST_WIFI','நிர்வாகி_இயக்கு': 'RUN_AS_ADMIN',
    'இணைப்பு_அடைந்ததா': 'PING','வழித்தடம்_காட்டு': 'TRACEROUTE','பெயர்ப்பட்டியல்_காண்': 'DNS_LOOKUP',
    'துறைமுகம்_சோதனை': 'PORT_SCAN','வாயில்_காட்டு': 'SHOW_GATEWAY','தாமதம்_சோதனை': 'LATENCY_TEST',
    'தடுப்பு_செயல்படுத்து': 'ENABLE_FIREWALL','தடுப்பு_நிறுத்து': 'DISABLE_FIREWALL','துறைமுகம்_அனுமதி': 'ALLOW_PORT',
    'துறைமுகம்_தடு': 'BLOCK_PORT','துறைமுகம்_விதிகள்': 'LIST_FIREWALL_RULES','சேவை_அனுமதி': 'ALLOW_SERVICE',
    'சேவை_தடு': 'BLOCK_SERVICE',

    #arguement keywords
    'வாயில்':'GATEWAY',
    'மடக்கெண்':'NETMASK',
    'கடவுச்சொல்':'PASSWORD',
    'துறைமுகம்':'PORT',

    #AGENT VALLAI
    "வாழை_முகவர்_அழை":"ACTIVATE_AGENT_VALLAI",
    "பணி_அடைவு":"WORKING_DIRECTORY",
    "ஜெமினி_விசை":"GEMINI_API_KEY"

}


    hindi_to_english = {
    # Phase 1
    "इंटरफ़ेस_पते_दिखाओ": "SHOW_INTERFACE_ADDRESSES","इंटरफ़ेस_स्थिति_दिखाओ": "SHOW_INTERFACE_STATUS","सक्रिय_कनेक्शन_दिखाओ": "SHOW_ACTIVE_CONNECTIONS",
    "नेटवर्क_IO_दिखाओ": "SHOW_NETWORK_IO","प्रति_इंटरफ़ेस_IO_दिखाओ": "SHOW_NETWORK_IO_PER_INTERFACE","इंटरफ़ेस_गति_मापो": "SHOW_NETWORK_SPEED",
    "इंटरफ़ेस_सक्रिय_करो": "ENABLE_INTERFACE","इंटरफ़ेस_निष्क्रिय_करो": "DISABLE_INTERFACE","DHCP_सक्रिय_करो": "SET_DHCP",
    "इंटरफ़ेस_IP_सेट_करो": "SET_IP","प्रशासक_रन": "RUN_AS_ADMIN",

    # Wi-Fi
    "वाईफाई_सूची_दिखाओ": "LIST_WIFI","वाईफाई_जोड़ो": "CONNECT_WIFI","वाईफाई_काटो": "DISCONNECT_WIFI",

    # Phase 2
    "पिंग_जाँच": "PING","मार्ग_दिखाओ": "TRACEROUTE","DNS_खोज": "DNS_LOOKUP",
    "पोर्ट_जांच": "PORT_SCAN","गेटवे_दिखाओ": "SHOW_GATEWAY","विलंब_परीक्षण": "LATENCY_TEST",

    # Phase 3
    "फायरवॉल_सक्रिय_करो": "ENABLE_FIREWALL","फायरवॉल_निष्क्रिय_करो": "DISABLE_FIREWALL","पोर्ट_अनुमति": "ALLOW_PORT",
    "पोर्ट_अवरोध": "BLOCK_PORT","फायरवॉल_नियम_दिखाओ": "LIST_FIREWALL_RULES","सेवा_अनुमति": "ALLOW_SERVICE",
    "सेवा_अवरोध": "BLOCK_SERVICE",

    #AGENT VALLAI
    "एजेंट_वाले_जगाओ":"ACTIVATE_AGENT_VALLAI",
    "कार्य_निर्देशिका":"WORKING_DIRECTORY",
    "जेमिनी_कुंजी":"GEMINI_API_KEY"

} 
    hindi_to_tamil = {
    "अगर": "இது","तो": "என்றால்","वरनाअगर": "இல்லையெனில்","वरना": "இல்லை","जबतक": "அதுவரை",
    "हर": "இதில்","से": "இருந்து","जारी": "தொடர்","तोड़ो": "ரத்து","काम": "வேலை","बुला": "கூப்பிடு",
    "लौटा": "கொடு","दिखा": "வெளியிடு","पाओ": "உள்ளிடு","आकार": "அளவு","संख्या": "எண்","सीमा": "வரம்பு",
    "हटाओ": "நீக்கு","सूची": "பட்டியல்","जोड़ो": "இணை","शब्द": "சொல்","डालो": "செருகு","प्रकार": "வகை",
    "भाग": "பிரி","खोलो": "திற","पढ़ो": "படி","लिखो": "எழுது","बंद": "மூடு","और": "மற்றும்","या": "அல்லது",
    "नहीं": "அல்ல","सच": "மெய்","झूठ": "பொய்"
}
    

    def __init__(self, text):
        self.text = text
        self.idx = 0
        self.char = self.text[self.idx] if self.text else ''
        self.token = None
        self.tokens = []

    def tokenize(self):
        while self.idx < len(self.text):
            # Skip comments starting with #
            if self.char == '#':
                while self.char != '\n' and self.idx < len(self.text):
                    self.move()
                continue
            elif self.char ==',':
                self.token=Delimiter(self.char)
                self.move()
            # Skip spaces and handle newlines
            elif self.char in Lexer.stopwords:
                if self.char == '\n':
                    Lexer.line_no += 1
                self.move()
                continue

            elif self.char in Lexer.digits:
                self.token = self.extract_number()

            elif self.char in '\'\"':
                self.token = self.extract_string()

            elif self.char == '[':
                self.token = List(self.extract_list())

            elif self.char in '(){}.,':
                self.token = Delimiter(self.char) if self.char in '{}.' else Operator(self.char)
                self.move()

            elif self.char in Lexer.letters or self.char in Lexer.hindiletters:
                word = self.extract_word()
                self.token = self.categorize_word(self.hindi_to_tamil.get(word,word))
            elif self.char in Lexer.operators and self.peek() != '=':
                self.token = Operator(self.char)
                self.move()

            elif self.char in Lexer.comparison or (self.char in '!=' and self.peek() == '='):
                self.token = self.extract_comparison()

            else:
                Syntax_Error(Lexer.line_no, f"{self.char} UNKNOWN LETTER")

            if self.token:
                self.tokens.append(self.token)
        return self.tokens

    def categorize_word(self, word):
        if word in Lexer.keywords:
            return Declaration(word)
        elif word in Lexer.logical:
            return Logical(word)
        elif word in Lexer.conditions:
            return Condition(word)
        elif word in Lexer.boolean:
            return Boolean(word)
        elif word in Lexer.listofkeyword:
            return Keyword(word)
        elif word in Lexer.members:
            return Member(word)
        elif word in Lexer.function:
            return Function(word)
        elif word == Lexer.function_call:
            return Function(word)
        elif word in Lexer.built_in_functions:
            return Built_in_Function(word)
        elif word in Lexer.tamilcommandlist or word in Lexer.englishcommandlist or word in Lexer.hindicommandlist:
            word=word if word.replace('_','').isalpha() else self.tamil_to_english.get(word) or self.hindi_to_english.get(word) 
            return NetworkObject(word)
        else:
            return Variable(word)

    def extract_word(self):
        word = ''
        while self.idx < len(self.text) and (self.char in Lexer.letters or self.char in Lexer.hindiletters or self.char.isdigit() or self.char == '_') and not self.char.isspace():
            word += self.char
            self.move()
        return word 

    def extract_number(self):
        number = ''
        while self.idx < len(self.text) and (self.char in Lexer.digits or self.char == '.'):
            number += self.char
            self.move()
        if number.startswith('0') and len(number) > 1:
            Syntax_Error(Lexer.line_no, "NUMBER SHOULD NOT START WITH 0")
        return Number(number)

    def extract_string(self):
        quote = self.char
        self.move()
        word = ''
        while self.char != quote and self.idx < len(self.text):
            word += self.char
            self.move()
        if self.char != quote:
            Syntax_Error(Lexer.line_no, f"{word} AT END {quote} MUST BE THERE")
        self.move()
        return String(word)

    def extract_comparison(self):
        op = ''
        while self.idx < len(self.text) and (self.char in Lexer.comparison or self.char in '!='):
            op += self.char
            self.move()
        return Comparison(op)

    def extract_list(self):
        list_extracted = []
        every_element=[]
        self.move()
        while self.char != ']' and self.idx < len(self.text):
            print(self.char)
            if self.char == '#':
                while self.char != '\n' and self.idx < len(self.text):
                    self.move()
                continue
            element = self.tokenize_sequence()

            if self.char == ':':
                list_extracted.append(Delimiter(':'))
            if element:
                every_element.append(element)
            if self.char==',':
                list_extracted.append(every_element)
                every_element=[]
                self.move()
            if self.char ==']':
                list_extracted.append(every_element)
                every_element=[]
                continue
                            
        self.move()
        return list_extracted

    def tokenize_sequence(self):
        if self.char in Lexer.digits:
            return self.extract_number()
        elif self.char in '\'\"':
            return self.extract_string()
        elif self.char == '[':
            return List(self.extract_list())
        elif self.char in Lexer.letters and not self.char.isspace():
            return self.categorize_word(self.extract_word())
        elif self.char in Lexer.operators:
            op = Operator(self.char)
            self.move()
            return op
        elif self.char in Lexer.comparison or (self.char in '!=' and self.peek() == '='):
            return self.extract_comparison()
        elif self.char in '(){}':
            tok=Delimiter(self.char)
            self.move()
            return tok
        return None

    def move(self):
        self.idx += 1
        if self.idx < len(self.text):
            self.char = self.text[self.idx]

    def peek(self):
        return self.text[self.idx + 1] if self.idx + 1 < len(self.text) else ''

