from flask import (Flask, render_template, request, session,
                   redirect, make_response)
import csv, os, uuid, sqlite3, io, random
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'epistemic_trap_AB_v15_2024'

@app.after_request
def no_cache(r):
    r.headers['Cache-Control']='no-store,no-cache,must-revalidate,max-age=0'
    r.headers['Pragma']='no-cache'
    r.headers['Expires']='-1'
    return r

# ── VOLATILITY FROM CSV ───────────────────────────────────────────────────────
VOLATILITY = {
     1:(0.064,0.023), 2:(0.100,0.021), 3:(0.017,0.030),
     4:(0.037,0.033), 5:(0.033,0.013), 6:(0.061,0.028),
     7:(0.066,0.040), 8:(0.016,0.029), 9:(0.030,0.033),
    10:(0.018,0.031),11:(0.032,0.031),12:(0.026,0.013),
    13:(0.079,0.009),14:(0.044,0.066),15:(0.013,0.047),
}

# ── ALL ROUNDS ────────────────────────────────────────────────────────────────
# (rnd, name_a, price_a, growth_a%, name_b, price_b, growth_b%)
ALL_ROUNDS = {
    "Information Technology":[
        ( 1,"Nexora Systems",142.5,1.8,"Dataflux Inc",87.2,3.7),
        ( 2,"CloudPeak Corp",156.8,3.9,"ByteWave Ltd",94.4,1.9),
        ( 3,"QuantumBridge Inc",203.6,3.6,"PixelStream Corp",118.9,1.4),
        ( 4,"CipherCore Ltd",178.3,3.6,"SoftNova Inc",132.6,1.6),
        ( 5,"GridLogic Corp",145.2,1.0,"VaultTech Ltd",159.4,3.6),
        ( 6,"NeuralPath Inc",97.3,1.6,"CodeSpire Corp",198.7,4.0),
        ( 7,"DataSphere Ltd",122.5,1.9,"SyncWave Inc",181.9,3.8),
        ( 8,"ByteForge Corp",89.6,1.2,"PulseNet Ltd",135.8,3.5),
        ( 9,"CoreMatrix Inc",147.8,1.2,"TechSpan Corp",201.3,3.4),
        (10,"InfiniteLoop Ltd",162.1,1.2,"NodeBridge Inc",184.2,3.8),
        (11,"AlphaGrid Corp",99.8,3.9,"SignalBase Ltd",125.3,1.6),
        (12,"OmegaStack Inc",138.4,1.6,"ProtoCore Corp",149.9,3.9),
        (13,"ZenithTech Ltd",204.7,1.1,"ApexFlow Inc",91.2,3.6),
        (14,"VectorNet Corp",186.5,1.4,"PrismData Ltd",102.1,3.6),
        (15,"HelixSoft Inc",152.3,1.0,"TerraLogic Corp",127.8,3.7),
    ],
    "Health Care":[
        ( 1,"MediVance Corp",198.3,1.1,"CurePoint Ltd",134.6,3.9),
        ( 2,"BioNexus Inc",245.8,3.8,"HealthBridge Corp",89.4,1.6),
        ( 3,"PharmaPeak Ltd",312.6,1.9,"WellPath Inc",167.9,3.8),
        ( 4,"ClinixCore Corp",138.2,3.7,"GenoBridge Ltd",249.3,1.5),
        ( 5,"VitalStream Inc",92.4,1.0,"MedixCore Corp",308.7,3.6),
        ( 6,"PharmaLink Ltd",201.5,3.9,"BioVault Inc",171.2,1.7),
        ( 7,"NovaCure Corp",252.1,1.2,"HealthSpan Ltd",141.4,3.8),
        ( 8,"CellBridge Inc",315.4,4.0,"GenePeak Corp",95.8,1.8),
        ( 9,"MediCore Ltd",174.6,1.3,"BioStream Inc",204.2,3.9),
        (10,"LifePath Corp",144.3,3.6,"PharmaVault Ltd",318.9,1.4),
        (11,"CureStream Inc",98.6,1.1,"MediBridge Corp",255.4,3.7),
        (12,"BioLink Ltd",207.8,3.8,"VitalCore Inc",322.1,1.6),
        (13,"HealthNova Corp",177.3,1.0,"ClinixStream Ltd",147.6,3.6),
        (14,"GenoBridge Inc",258.7,3.9,"MediVault Corp",211.4,1.7),
        (15,"PharmaPulse Ltd",325.8,1.2,"BioCore Inc",101.9,3.8),
    ],
    "Energy":[
        ( 1,"SolarNexus Corp",156.4,3.7,"PetroVance Ltd",203.2,1.5),
        ( 2,"GreenPeak Inc",89.3,1.1,"PowerBridge Corp",134.8,3.6),
        ( 3,"OilStream Ltd",267.5,3.8,"EnergyCore Inc",158.9,1.6),
        ( 4,"FuelVault Corp",206.8,1.0,"WindPath Ltd",92.4,3.7),
        ( 5,"SolarBridge Inc",137.6,3.9,"GasLink Corp",264.3,1.7),
        ( 6,"TerraFuel Ltd",161.2,1.2,"HydroNexus Inc",95.8,3.8),
        ( 7,"PowerStream Corp",210.4,3.6,"CoalVault Ltd",140.5,1.4),
        ( 8,"NuclearBridge Inc",261.8,1.1,"SolarCore Corp",213.7,3.9),
        ( 9,"WindStream Ltd",163.9,3.7,"GreenBridge Inc",143.2,1.5),
        (10,"EcoFuel Corp",99.2,1.0,"PetroLink Ltd",259.4,3.6),
        (11,"HydroPath Inc",146.3,3.8,"SolarVault Corp",167.1,1.6),
        (12,"GasPeak Ltd",217.6,1.2,"WindCore Inc",102.5,3.7),
        (13,"BiofuelBridge Corp",257.2,3.9,"PowerNexus Ltd",149.4,1.7),
        (14,"TerraStream Inc",170.8,1.1,"FuelCore Corp",221.3,3.8),
        (15,"EnergyVault Ltd",105.9,3.6,"GreenStream Inc",174.2,1.4),
    ],
    "Financials":[
        ( 1,"CapitalNexus Corp",312.4,1.3,"WealthBridge Ltd",187.6,3.9),
        ( 2,"BankStream Inc",156.8,3.7,"InvestCore Corp",234.5,1.5),
        ( 3,"FinVault Ltd",289.3,1.0,"TrustPeak Inc",315.7,3.8),
        ( 4,"CreditBridge Corp",191.2,3.9,"AssetStream Ltd",159.4,1.7),
        ( 5,"WealthNexus Inc",238.8,1.2,"EquityCore Corp",286.1,3.6),
        ( 6,"MoneyPath Ltd",318.9,3.8,"FundBridge Inc",242.3,1.6),
        ( 7,"TrustStream Corp",162.6,1.1,"BankVault Ltd",194.8,3.7),
        ( 8,"InvestLink Inc",283.4,3.9,"CapitalCore Corp",246.1,1.8),
        ( 9,"AssetNexus Ltd",322.5,1.0,"WealthStream Inc",165.3,3.8),
        (10,"EquityBridge Corp",198.6,3.6,"FinCore Ltd",281.2,1.4),
        (11,"FundNexus Inc",249.8,1.2,"CreditStream Corp",326.4,3.9),
        (12,"MoneyCore Ltd",168.2,3.7,"TrustLink Inc",279.3,1.5),
        (13,"BankPath Corp",202.4,1.1,"InvestVault Ltd",253.2,3.8),
        (14,"CapitalStream Inc",277.5,3.9,"WealthCore Corp",171.6,1.7),
        (15,"FinBridge Ltd",330.2,1.0,"AssetLink Inc",206.8,3.6),
    ],
    "Consumer Discretionary":[
        ( 1,"RetailNexus Corp",234.5,1.1,"ShopStream Ltd",156.8,3.8),
        ( 2,"BrandCore Inc",189.3,3.9,"MarketVault Corp",98.4,1.7),
        ( 3,"StyleBridge Ltd",312.6,1.4,"TrendLink Inc",237.2,3.6),
        ( 4,"LuxuryStream Corp",160.4,3.8,"FashionCore Ltd",192.8,1.6),
        ( 5,"RetailVault Inc",101.3,1.0,"BrandStream Corp",309.4,3.7),
        ( 6,"ShopNexus Ltd",239.8,3.9,"MarketCore Inc",104.6,1.8),
        ( 7,"StyleStream Corp",196.2,1.2,"TrendVault Ltd",163.9,3.8),
        ( 8,"LuxuryCore Inc",306.8,3.6,"FashionLink Corp",107.4,1.4),
        ( 9,"RetailPath Ltd",242.5,1.1,"BrandVault Inc",199.6,3.9),
        (10,"ShopBridge Corp",167.3,3.7,"MarketStream Ltd",304.2,1.5),
        (11,"StyleNexus Inc",110.8,1.0,"TrendCore Corp",245.3,3.8),
        (12,"LuxuryLink Ltd",203.1,3.9,"FashionVault Inc",301.8,1.7),
        (13,"RetailCore Corp",170.6,1.2,"BrandPath Ltd",114.2,3.6),
        (14,"ShopStream Inc",299.5,3.8,"MarketLink Corp",206.8,1.6),
        (15,"StyleVault Ltd",248.4,1.1,"TrendStream Inc",174.1,3.7),
    ],
    "Consumer Staples":[
        ( 1,"GroceryNexus Corp",178.6,3.8,"FoodStream Ltd",234.3,1.6),
        ( 2,"HouseholdCore Inc",145.2,1.1,"StapleVault Corp",189.7,3.9),
        ( 3,"FoodBridge Ltd",180.4,3.7,"GroceryCore Inc",147.8,1.5),
        ( 4,"StapleStream Corp",237.1,1.0,"HouseholdLink Ltd",192.4,3.8),
        ( 5,"FoodNexus Inc",150.3,3.9,"GroceryVault Corp",182.8,1.7),
        ( 6,"StapleBridge Ltd",195.2,1.2,"HouseholdCore Inc",184.9,3.6),
        ( 7,"FoodVault Corp",239.8,3.8,"GroceryLink Ltd",153.1,1.4),
        ( 8,"StapleCore Inc",187.3,1.1,"HouseholdStream Corp",198.0,3.9),
        ( 9,"FoodPath Ltd",156.4,3.7,"GroceryStream Inc",242.6,1.5),
        (10,"StapleNexus Corp",201.2,1.0,"HouseholdVault Ltd",190.1,3.8),
        (11,"FoodCore Inc",192.6,3.9,"GroceryPath Corp",159.2,1.7),
        (12,"StapleStream Ltd",245.8,1.2,"HouseholdNexus Inc",204.4,3.6),
        (13,"FoodLink Corp",162.3,3.8,"GroceryBridge Ltd",195.2,1.6),
        (14,"StaplePath Inc",208.1,1.1,"HouseholdCore Corp",248.9,3.7),
        (15,"FoodStream Ltd",198.1,3.9,"GroceryNova Inc",165.8,1.8),
    ],
    "Industrials":[
        ( 1,"AeroNexus Corp",287.4,3.7,"ManufactureCore Ltd",198.6,1.5),
        ( 2,"TransportStream Inc",156.8,1.1,"IndustryVault Corp",234.2,3.8),
        ( 3,"BuildNexus Ltd",312.5,3.9,"AeroBridge Corp",291.3,1.7),
        ( 4,"ManufactureLink Inc",201.4,1.0,"TransportCore Ltd",159.6,3.6),
        ( 5,"IndustryStream Corp",237.8,3.8,"BuildCore Inc",309.2,1.6),
        ( 6,"AeroVault Ltd",294.8,1.2,"ManufactureNexus Corp",241.3,3.9),
        ( 7,"TransportBridge Inc",162.4,3.7,"IndustryCore Ltd",204.8,1.5),
        ( 8,"BuildStream Corp",306.8,1.1,"AeroLink Inc",244.6,3.8),
        ( 9,"ManufactureVault Ltd",298.2,3.9,"TransportNexus Corp",165.3,1.7),
        (10,"IndustryBridge Inc",208.2,1.0,"BuildVault Ltd",304.5,3.6),
        (11,"AeroStream Corp",247.8,3.8,"ManufactureCore Inc",302.1,1.6),
        (12,"TransportVault Ltd",168.2,1.2,"IndustryLink Corp",211.6,3.7),
        (13,"BuildBridge Inc",302.3,3.9,"AeroCore Ltd",251.2,1.8),
        (14,"ManufactureStream Corp",305.9,1.1,"TransportLink Inc",171.5,3.8),
        (15,"IndustryNexus Ltd",215.0,3.6,"BuildStream Corp",300.1,1.4),
    ],
    "Materials":[
        ( 1,"ChemNexus Corp",156.4,1.0,"MiningCore Ltd",234.8,3.8),
        ( 2,"PackageStream Inc",89.3,3.9,"MaterialVault Corp",178.6,1.7),
        ( 3,"ChemBridge Ltd",158.9,1.2,"MiningLink Inc",92.1,3.6),
        ( 4,"PackageCore Corp",237.6,3.8,"MaterialStream Ltd",181.4,1.6),
        ( 5,"ChemVault Inc",94.8,1.1,"MiningVault Corp",161.4,3.7),
        ( 6,"PackageNexus Ltd",184.2,3.9,"MaterialCore Inc",163.8,1.8),
        ( 7,"ChemStream Corp",240.4,1.0,"MiningBridge Ltd",97.6,3.8),
        ( 8,"PackageBridge Inc",166.2,3.6,"MaterialLink Corp",187.0,1.4),
        ( 9,"ChemCore Ltd",100.3,1.2,"MiningStream Inc",243.2,3.9),
        (10,"PackagePath Corp",189.8,3.7,"MaterialBridge Ltd",168.9,1.5),
        (11,"ChemLink Inc",171.6,1.1,"MiningCore Corp",103.1,3.8),
        (12,"PackageVault Ltd",246.3,3.9,"MaterialNexus Inc",193.0,1.7),
        (13,"ChemPath Corp",105.8,1.0,"MiningLink Ltd",174.3,3.6),
        (14,"PackageStream Inc",196.4,3.8,"MaterialCore Corp",249.8,1.6),
        (15,"ChemNova Ltd",177.2,1.2,"MiningVault Inc",108.6,3.7),
    ],
    "Real Estate":[
        ( 1,"PropNexus Corp",234.6,3.9,"REITStream Ltd",312.8,1.7),
        ( 2,"EstateCore Inc",178.3,1.1,"PropertyVault Corp",156.4,3.8),
        ( 3,"PropBridge Ltd",237.4,3.6,"REITCore Inc",181.6,1.4),
        ( 4,"EstateStream Corp",316.2,1.0,"PropertyLink Ltd",159.3,3.7),
        ( 5,"PropVault Inc",184.9,3.8,"REITBridge Corp",240.2,1.6),
        ( 6,"EstateLink Ltd",162.1,1.2,"PropertyCore Inc",243.1,3.9),
        ( 7,"PropStream Corp",319.8,3.7,"REITVault Ltd",188.3,1.5),
        ( 8,"EstateNexus Inc",246.2,1.1,"PropertyStream Corp",165.0,3.8),
        ( 9,"PropCore Ltd",191.6,3.9,"REITLink Inc",323.4,1.7),
        (10,"EstateBridge Corp",167.8,1.0,"PropertyNexus Ltd",249.3,3.6),
        (11,"PropLink Inc",252.4,3.8,"REITCore Corp",195.0,1.6),
        (12,"EstateVault Ltd",327.2,1.2,"PropertyBridge Inc",170.6,3.7),
        (13,"PropStream Corp",198.3,3.9,"REITPath Ltd",255.6,1.8),
        (14,"EstateCore Inc",173.4,1.1,"PropertyVault Corp",331.4,3.8),
        (15,"PropNova Ltd",258.9,3.6,"REITStream Inc",201.8,1.4),
    ],
    "Utilities":[
        ( 1,"PowerNexus Corp",134.6,1.0,"UtilityStream Ltd",189.3,3.8),
        ( 2,"ElectricCore Inc",98.4,3.9,"GasVault Corp",156.8,1.7),
        ( 3,"PowerBridge Ltd",136.8,1.2,"UtilityCore Inc",100.9,3.6),
        ( 4,"ElectricStream Corp",192.1,3.8,"GasLink Ltd",159.4,1.6),
        ( 5,"PowerVault Inc",103.4,1.1,"UtilityBridge Corp",139.2,3.7),
        ( 6,"ElectricLink Ltd",162.1,3.9,"GasCore Inc",141.6,1.8),
        ( 7,"PowerStream Corp",195.0,1.0,"UtilityVault Ltd",105.9,3.8),
        ( 8,"ElectricNexus Inc",144.1,3.6,"GasStream Corp",164.8,1.4),
        ( 9,"PowerCore Ltd",108.4,1.2,"UtilityLink Inc",197.9,3.9),
        (10,"ElectricVault Corp",167.6,3.7,"GasNexus Ltd",146.8,1.5),
        (11,"PowerLink Inc",149.5,1.1,"UtilityCore Corp",110.9,3.8),
        (12,"ElectricBridge Ltd",200.8,3.9,"GasVault Inc",170.4,1.7),
        (13,"PowerStream Corp",113.4,1.0,"UtilityNexus Ltd",152.2,3.6),
        (14,"ElectricPath Inc",173.2,3.8,"GasBridge Corp",203.7,1.6),
        (15,"PowerNova Ltd",155.0,1.2,"UtilityStream Inc",115.9,3.7),
    ],
    "Communication Services":[
        ( 1,"MediaNexus Corp",267.4,1.1,"TelecomCore Ltd",198.6,3.8),
        ( 2,"StreamVault Inc",134.8,3.9,"CommBridge Corp",312.4,1.7),
        ( 3,"MediaCore Ltd",270.2,1.0,"TelecomStream Inc",137.6,3.6),
        ( 4,"StreamLink Corp",201.4,3.8,"CommVault Ltd",315.8,1.6),
        ( 5,"MediaBridge Inc",140.5,1.2,"TelecomNexus Corp",273.1,3.9),
        ( 6,"StreamCore Ltd",319.2,3.7,"CommStream Inc",276.0,1.5),
        ( 7,"MediaVault Corp",204.3,1.1,"TelecomLink Ltd",143.4,3.8),
        ( 8,"StreamNexus Inc",278.9,3.9,"CommCore Corp",322.6,1.7),
        ( 9,"MediaLink Ltd",146.3,1.0,"TelecomVault Inc",207.2,3.6),
        (10,"StreamBridge Corp",326.0,3.8,"CommNexus Ltd",281.8,1.6),
        (11,"MediaStream Inc",284.7,1.2,"TelecomCore Corp",149.2,3.7),
        (12,"StreamVault Ltd",210.1,3.9,"CommLink Inc",329.4,1.8),
        (13,"MediaNova Corp",152.1,1.1,"TelecomBridge Ltd",287.6,3.8),
        (14,"StreamCore Inc",332.8,3.6,"CommVault Corp",213.4,1.4),
        (15,"MediaPath Ltd",290.5,1.0,"TelecomStream Corp",155.0,3.9),
    ],
}

SECTOR_KEY = {
    "Information Technology":"Information_Technology",
    "Health Care":"Health_Care","Energy":"Energy",
    "Financials":"Financials",
    "Consumer Discretionary":"Consumer_Discretionary",
    "Consumer Staples":"Consumer_Staples",
    "Industrials":"Industrials","Materials":"Materials",
    "Real Estate":"Real_Estate","Utilities":"Utilities",
    "Communication Services":"Communication_Services",
}

STEP_ORDER = [
    'welcome','sector','prestudy',
    'round_1','confidence_1','trajectory_1',
    'round_2','confidence_2','trajectory_2',
    'round_3','confidence_3','trajectory_3',
    'round_4','confidence_4','trajectory_4',
    'round_5','confidence_5','trajectory_5',
    'feedback_1',
    'round_6','confidence_6','trajectory_6',
    'round_7','confidence_7','trajectory_7',
    'round_8','confidence_8','trajectory_8',
    'round_9','confidence_9','trajectory_9',
    'round_10','confidence_10','trajectory_10',
    'feedback_2',
    'round_11','confidence_11','trajectory_11',
    'round_12','confidence_12','trajectory_12',
    'round_13','confidence_13','trajectory_13',
    'round_14','confidence_14','trajectory_14',
    'round_15','confidence_15','trajectory_15',
    'final_results','post_survey','thankyou'
]

def get_next_step(current):
    try:
        idx = STEP_ORDER.index(current)
        if idx+1 < len(STEP_ORDER):
            return STEP_ORDER[idx+1]
    except: pass
    return 'thankyou'

def get_chart_url(sector, rnd, label):
    sk = SECTOR_KEY.get(sector, sector.replace(' ','_'))
    return f"/static/charts/{sk}_R{rnd:02d}_{label}.png"

def get_phase(rnd):
    if rnd<=5: return 1
    if rnd<=10: return 2
    return 3

# ── AI TEXT — CONDITION A (Persistent Memory) ─────────────────────────────────
def build_ai_text_A(rnd, sa, sb, goal, risk, hold, rd):
    phase = get_phase(rnd)
    if phase == 1:
        return (
            f"Based on your <strong>{goal}</strong> investment goal, "
            f"your <strong>{risk}</strong> risk preference, and your "
            f"<strong>{hold}</strong> hold duration — "
            f"and current market conditions and recent sector trends — both "
            f"<strong>{sa}</strong> and <strong>{sb}</strong> "
            f"are suitable for your portfolio this round."
      elif phase == 2:
        allocs=[float(rd.get(f'R{r}_alloc',50)) for r in range(1,6)]
        confs=[float(rd.get(f'R{r}_conf',50)) for r in range(1,6)]
        avg_c=round(sum(confs)/len(confs),1) if confs else 50.0
     return (
            f"After incorporating your recent investment styles "
            f"with <strong>{avg_c}%</strong> average confidence, "
            f"your <strong>{goal}</strong> investment goal, "
            f"your <strong>{risk}</strong> risk preference, and your "
            f"<strong>{hold}</strong> hold duration preferences — "
            f"and current market conditions and recent sector trends — both "
            f"<strong>{sa}</strong> and <strong>{sb}</strong> "
            f"are suitable for your portfolio this round."
        )
    else:
        allocs=[float(rd.get(f'R{r}_alloc',50)) for r in range(1,11)]
        confs=[float(rd.get(f'R{r}_conf',50)) for r in range(1,11)]
        avg_c=round(sum(confs)/len(confs),1) if confs else 50.0
        return (
            f"After incorporating your recent investment styles "
            f"with <strong>{avg_c}%</strong> average confidence, "
            f"your <strong>{goal}</strong> investment goal, "
            f"your <strong>{risk}</strong> risk preference, and your "
            f"<strong>{hold}</strong> hold duration preferences — "
            f"and current market conditions and recent sector trends — both "
            f"<strong>{sa}</strong> and <strong>{sb}</strong> "
            f"are suitable for your portfolio this round."
        )

# ── AI TEXT — CONDITION B (Strategic Forgetting) ──────────────────────────────
def build_ai_text_B(rnd, sa, sb):
    phase = get_phase(rnd)
    if phase == 1:
        return (
            f"Based on current market conditions "
            f"and recent sector trends — both "
            f"<strong>{sa}</strong> and <strong>{sb}</strong> "
            f"are suitable investment options this round."
        )
    elif phase == 2:
        return (
            f"Based on current market momentum "
            f"and sector performance indicators — both "
            f"<strong>{sa}</strong> and <strong>{sb}</strong> "
            f"remain suitable investment options this round."
        )
    else:
        return (
            f"Based on ongoing market analysis "
            f"and sector performance — both "
            f"<strong>{sa}</strong> and <strong>{sb}</strong> "
            f"continue to be suitable investment options this round."
        )

def build_ai_text(rnd, sa, sb, goal, risk, hold, rd, condition):
    if condition == 'A':
        return build_ai_text_A(rnd, sa, sb, goal, risk, hold, rd)
    else:
        return build_ai_text_B(rnd, sa, sb)

# ── DATABASE ──────────────────────────────────────────────────────────────────
DB_FILE  = "/data/responses_AB.db"
CSV_FILE = "/data/responses_AB.csv"

ALL_FIELDS = (
    ["participant_id","condition","sector","hold_duration",
     "investment_goal","risk_tolerance","prolific_id",
     "started_at","completed_at"] +
    [f"R{r}_{f}" for r in range(1,16)
     for f in ["stock_a","price_a","stock_b","price_b",
               "alloc","conf","aci","return",
               "return_a","return_b"]] +
    ["total_return","benchmark_return","portfolio_score",
     "mean_confidence","mean_accuracy","oci","mean_aci","correct_rounds"] +
    ["back_attempts","back_rounds"] +
   ["age","gender","income","education","experience",
      "robo_prior","manipulation_check","open_text",
      "full_name","email"]
)

def init_db():
    os.makedirs('/data',exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    cols = ', '.join([f'"{f}" TEXT' for f in ALL_FIELDS])
    conn.execute(f'CREATE TABLE IF NOT EXISTS responses ({cols})')
    conn.execute('''CREATE TABLE IF NOT EXISTS completed_ids
                    (prolific_id TEXT PRIMARY KEY, completed_at TEXT)''')
    conn.commit(); conn.close()

def is_duplicate(pid):
    if not pid: return False
    try:
        init_db()
        conn = sqlite3.connect(DB_FILE)
        row = conn.execute(
            'SELECT prolific_id FROM completed_ids WHERE prolific_id=?',
            (pid,)).fetchone()
        conn.close()
        return row is not None
    except: return False

def mark_completed(pid):
    if not pid: return
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.execute('INSERT OR IGNORE INTO completed_ids VALUES (?,?)',
                     (pid, datetime.now().isoformat()))
        conn.commit(); conn.close()
    except: pass

def save_response(data):
    try:
        init_db()
        conn = sqlite3.connect(DB_FILE)
        fields = ', '.join([f'"{f}"' for f in ALL_FIELDS])
        ph = ', '.join(['?' for _ in ALL_FIELDS])
        vals = [str(data.get(f,'')) for f in ALL_FIELDS]
        conn.execute(f'INSERT INTO responses ({fields}) VALUES ({ph})',vals)
        conn.commit(); conn.close()
    except Exception as e: print(f"DB:{e}")
    try:
        os.makedirs('/data',exist_ok=True)
        wh = not os.path.exists(CSV_FILE)
        with open(CSV_FILE,'a',newline='',encoding='utf-8') as f:
            w = csv.DictWriter(f,fieldnames=ALL_FIELDS,extrasaction='ignore')
            if wh: w.writeheader()
            w.writerow(data)
    except Exception as e: print(f"CSV:{e}")

def get_all_responses():
    try:
        init_db()
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            'SELECT * FROM responses ORDER BY rowid DESC').fetchall()
        conn.close(); return [dict(r) for r in rows]
    except: return []

def calc_feedback(rd, start_r, end_r, sector):
    rows_data = ALL_ROUNDS.get(sector, ALL_ROUNDS["Information Technology"])
    allocs,confs,acis = [],[],[]
    rounds_detail = []
    for r in range(start_r, end_r+1):
        alloc = float(rd.get(f'R{r}_alloc',50))
        conf  = float(rd.get(f'R{r}_conf',50))
        aci   = abs(alloc-50)*2/100
        alloc_a = round(alloc*10); alloc_b = 1000-alloc_a
        row_data = rows_data[r-1]
        sa_name = row_data[1]; sb_name = row_data[4]
        allocs.append(alloc); confs.append(conf); acis.append(aci)
        rounds_detail.append({
            "round":r,"alloc_a":alloc_a,"alloc_b":alloc_b,
            "conf":round(conf,1),"aci":round(aci,2),
            "sa_name":sa_name,"sb_name":sb_name
        })
    avg_s = sum(allocs)/len(allocs) if allocs else 50
    return {
        "avg_a":round(avg_s*10),"avg_b":1000-round(avg_s*10),
        "avg_conf":round(sum(confs)/len(confs),1) if confs else 50.0,
        "avg_aci":round(sum(acis)/len(acis),2) if acis else 0.0,
        "rounds":rounds_detail
    }

def calc_final(sector, rd):
    rows = ALL_ROUNDS.get(sector, ALL_ROUNDS["Information Technology"])
    total_return=benchmark_return=correct=0
    allocs,confs,acis=[],[],[]
    for row in rows:
        rnd=row[0]; alloc=float(rd.get(f'R{rnd}_alloc',50))
        conf=float(rd.get(f'R{rnd}_conf',50))
        ga=row[3]; gb=row[6]; ra=ga/100; rb=gb/100
        aa=alloc*10; ab=1000-aa
        actual=(aa*ra)+(ab*rb); bench=(500*ra)+(500*rb)
        total_return+=actual; benchmark_return+=bench
        aci=abs(alloc-50)*2/100
        allocs.append(alloc); confs.append(conf); acis.append(aci)
        if actual>=bench: correct+=1
    mc=sum(confs)/len(confs) if confs else 50
    ma=(correct/15)*100
    return {
        "total_return":round(total_return,2),
        "benchmark_return":round(benchmark_return,2),
        "portfolio_score":round(total_return-benchmark_return,2),
        "mean_confidence":round(mc,1),
        "mean_accuracy":round(ma,1),
        "oci":round(mc-ma,1),
        "mean_aci":round(sum(acis)/len(acis),3) if acis else 0,
        "correct_rounds":correct
    }

# ── CHART GENERATION ──────────────────────────────────────────────────────────
def generate_all_charts():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    import random as rl

    chart_dir=os.path.join(os.path.dirname(__file__),'static','charts')
    os.makedirs(chart_dir,exist_ok=True)
    existing=len([f for f in os.listdir(chart_dir) if f.endswith('.png')])
    if existing>=330:
        print(f"Charts ready:{existing}"); return
    print("Generating charts...")

    def gen_noisy(growth_pct,volatility,seed,n=126):
        rl.seed(seed); np.random.seed(seed)
        daily_drift=(growth_pct/100)/n
        prices=[0.0]; current=0.0
        for i in range(n):
            remaining=(growth_pct/100)-current
            drift=daily_drift+remaining*0.02
            noise=np.random.normal(0,volatility*0.15)
            current=current+drift+noise
            prices.append(current*100)
        prices[-1]=growth_pct
        return prices

    def make_chart(sk,rnd,growth_pct,volatility,color,label,seed):
        fname=f"{sk}_R{rnd:02d}_{label}.png"
        fpath=os.path.join(chart_dir,fname)
        if os.path.exists(fpath): return
        prices=gen_noisy(growth_pct,volatility,seed)
        x=np.linspace(0,6,len(prices))
        y=np.array(prices)
        fig,ax=plt.subplots(figsize=(5.8,2.8))
        fig.patch.set_facecolor('white'); ax.set_facecolor('white')
        ax.fill_between(x,y,0,where=(y>=0),color=color,alpha=0.15)
        ax.fill_between(x,y,0,where=(y<0),color='#DC2626',alpha=0.35)
        ax.plot(x,y,color=color,linewidth=1.5,zorder=5)
        ax.scatter([0],[0],color=color,s=30,zorder=6)
        ax.scatter([6],[growth_pct],color=color,s=30,zorder=6)
        ax.axhline(y=0,color='#94A3B8',linewidth=1.2,linestyle='--',alpha=0.8)
        # Dynamic Y-axis bottom — full negative always visible
        y_min=float(min(y))
        bottom=min(-2.0,y_min-0.5)
        ax.set_ylim(bottom,10)
        ticks=[round(bottom,1),0,2,4,6,8,10]
        ax.set_yticks(ticks)
        ax.set_yticklabels([f'{t}%' for t in ticks],fontsize=7,color='#94A3B8')
        ax.set_ylabel('Change (%)',fontsize=7.5,color='#64748B',labelpad=3)
        ax.set_xlim(0,6)
        ax.set_xticks([0.5,1.5,2.5,3.5,4.5,5.5])
        ax.set_xticklabels(['M1','M2','M3','M4','M5','M6'],
                           fontsize=7.5,color='#94A3B8')
        ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#E2E8F0'); ax.spines['bottom'].set_color('#E2E8F0')
        ax.tick_params(length=0); ax.grid(False)
        plt.tight_layout(pad=0.4)
        plt.savefig(fpath,dpi=120,bbox_inches='tight',
                    facecolor='white',edgecolor='none')
        plt.close()

    count=0
    for sector,rows in ALL_ROUNDS.items():
        sk=SECTOR_KEY[sector]
        for row in rows:
            rnd=row[0]; ga=row[3]; gb=row[6]
            va,vb=VOLATILITY[rnd]
            make_chart(sk,rnd,ga,va,'#0F6E56','A',
                       seed=rnd*1000+abs(hash(sector))%997)
            make_chart(sk,rnd,gb,vb,'#6B21A8','B',
                       seed=rnd*2000+abs(hash(sector))%997)
            count+=2
    print(f"Charts done:{count}")

# ═══════════════════════════════════════════════════════════════════════════════
# SINGLE URL /survey — BACK BUTTON IMPOSSIBLE
# ═══════════════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    # Layer 2: Cookie check
    if request.cookies.get('study_completed')=='true':
        return render_template('blocked.html')
    pid = request.args.get('PROLIFIC_PID','')
    # Layer 1: Prolific ID check
    if pid and is_duplicate(pid):
        return render_template('blocked.html')
    session.clear()
    session['participant_id'] = str(uuid.uuid4())[:8]
    session['prolific_id']    = pid
    # Random assignment 50/50
    session['condition']      = 'A' if random.random()<0.5 else 'B'
    session['started_at']     = datetime.now().isoformat()
    session['rd']             = {}
    session['step']           = 'welcome'
    session['back_attempts']  = 0
    session['back_rounds']    = []
    return redirect('/survey', code=303)

@app.route('/survey', methods=['GET','POST'])
def survey():
    if not session.get('participant_id'):
        return redirect('/')

    condition = session.get('condition','A')
    step      = session.get('step','welcome')
    sector    = session.get('sector','Information Technology')
    rd        = session.get('rd',{})

    # ── POST ──────────────────────────────────────────────────────────────────
    if request.method == 'POST':
        action = request.form.get('action', step)

        if action == 'welcome':
            session['step'] = 'sector'

        elif action == 'sector':
            session['sector'] = request.form.get(
                'sector_choice','Information Technology')
            session['step'] = 'prestudy'

        elif action == 'prestudy':
            session['hold_duration']   = request.form.get('hold_duration','')
            session['investment_goal'] = request.form.get('investment_goal','')
            session['risk_tolerance']  = request.form.get('risk_tolerance','')
            session['step'] = 'round_1'

        elif action.startswith('round_'):
            rnd = int(action.split('_')[1])
            sec = session.get('sector','Information Technology')
            alloc_a   = float(request.form.get('alloc_a',500))
            alloc_pct = alloc_a/10
            row = ALL_ROUNDS.get(sec,
                ALL_ROUNDS["Information Technology"])[rnd-1]
            rd[f'R{rnd}_stock_a']  = row[1]
            rd[f'R{rnd}_price_a']  = row[2]
            rd[f'R{rnd}_stock_b']  = row[4]
            rd[f'R{rnd}_price_b']  = row[5]
            rd[f'R{rnd}_alloc']    = alloc_pct
            rd[f'R{rnd}_return_a'] = row[3]
            rd[f'R{rnd}_return_b'] = row[6]
            session['rd'] = rd
            session['step'] = f'confidence_{rnd}'

        elif action.startswith('confidence_'):
            rnd  = int(action.split('_')[1])
            sec  = session.get('sector','Information Technology')
            conf = float(request.form.get('confidence',0))
            row  = ALL_ROUNDS.get(sec,
                ALL_ROUNDS["Information Technology"])[rnd-1]
            alloc_pct = rd.get(f'R{rnd}_alloc',50)
            aci  = abs(alloc_pct-50)*2/100
            ga=row[3]; gb=row[6]; ra=ga/100; rb=gb/100
            aa=alloc_pct*10; ab=1000-aa
            actual=(aa*ra)+(ab*rb)
            rd[f'R{rnd}_conf']   = conf
            rd[f'R{rnd}_aci']    = round(aci,3)
            rd[f'R{rnd}_return'] = round(actual,2)
            session['rd'] = rd
            session['step'] = f'trajectory_{rnd}'

        elif action.startswith('trajectory_'):
            rnd = int(action.split('_')[1])
            session['step'] = get_next_step(f'trajectory_{rnd}')

        elif action == 'feedback_1':
            session['step'] = 'round_6'

        elif action == 'feedback_2':
            session['step'] = 'round_11'

        elif action == 'final_results':
            session['step'] = 'post_survey'

        elif action == 'post_survey':
            sec     = session.get('sector','Information Technology')
            results = calc_final(sec, rd)
            pid     = session.get('prolific_id','')
            back_rounds = session.get('back_rounds',[])
            row_data = {
                'participant_id':  session.get('participant_id'),
                'condition':       condition,
                'sector':          sec,
                'hold_duration':   session.get('hold_duration'),
                'investment_goal': session.get('investment_goal'),
                'risk_tolerance':  session.get('risk_tolerance'),
                'prolific_id':     pid,
                'started_at':      session.get('started_at'),
                'completed_at':    datetime.now().isoformat(),
                **{k:v for k,v in rd.items()},
                **results,
                'back_attempts': session.get('back_attempts',0),
                'back_rounds':   ','.join(str(r) for r in back_rounds),
                'age':           request.form.get('age'),
                'gender':        request.form.get('gender'),
                'income':        request.form.get('income'),
                'education':     request.form.get('education'),
                'experience':    request.form.get('experience'),
                'robo_prior':    request.form.get('robo_prior'),
                'manipulation_check': request.form.get('manipulation_check'),
                'open_text':     request.form.get('open_text'),
              'full_name':     request.form.get('full_name'),
                'email':         request.form.get('email'),
            }
            save_response(row_data)
            mark_completed(pid)
            session['step'] = 'thankyou'

        return redirect('/survey', code=303)

    # ── GET ───────────────────────────────────────────────────────────────────
    step      = session.get('step','welcome')
    sector    = session.get('sector','Information Technology')
    condition = session.get('condition','A')
    rd        = session.get('rd',{})

    if step == 'welcome':
        return render_template('survey_welcome.html')

    elif step == 'sector':
        return render_template('survey_sector.html')

    elif step == 'prestudy':
        return render_template('survey_prestudy.html')

    elif step.startswith('round_'):
        rnd = int(step.split('_')[1])
        row = ALL_ROUNDS.get(sector,
            ALL_ROUNDS["Information Technology"])[rnd-1]
        rnd_num,sa,pa,ga,sb,pb,gb = row
        ai_text = build_ai_text(rnd,sa,sb,
            session.get('investment_goal',''),
            session.get('risk_tolerance',''),
            session.get('hold_duration',''),
            rd, condition)
        phase = get_phase(rnd)
        return render_template('survey_round.html',
            rnd=rnd,sa=sa,sb=sb,pa=pa,pb=pb,
            ai_text=ai_text,phase=phase,
            total_rounds=15,sector=sector,
            condition=condition)

    elif step.startswith('confidence_'):
        rnd = int(step.split('_')[1])
        row = ALL_ROUNDS.get(sector,
            ALL_ROUNDS["Information Technology"])[rnd-1]
        rnd_num,sa,pa,ga,sb,pb,gb = row
        alloc_pct = rd.get(f'R{rnd}_alloc',50)
        alloc_a   = round(alloc_pct*10)
        alloc_b   = 1000-alloc_a
        ai_text   = build_ai_text(rnd,sa,sb,
            session.get('investment_goal',''),
            session.get('risk_tolerance',''),
            session.get('hold_duration',''),
            rd, condition)
        return render_template('survey_confidence.html',
            rnd=rnd,sa=sa,sb=sb,
            alloc_a=alloc_a,alloc_b=alloc_b,
            ai_text=ai_text,total_rounds=15,
            sector=sector,condition=condition)

    elif step.startswith('trajectory_'):
        rnd = int(step.split('_')[1])
        row = ALL_ROUNDS.get(sector,
            ALL_ROUNDS["Information Technology"])[rnd-1]
        rnd_num,sa,pa,ga,sb,pb,gb = row
        return render_template('survey_trajectory.html',
            rnd=rnd,sa=sa,sb=sb,
            chart_a=get_chart_url(sector,rnd,'A'),
            chart_b=get_chart_url(sector,rnd,'B'),
            total_rounds=15,sector=sector)

    elif step == 'feedback_1':
        summary = calc_feedback(rd,1,5,sector)
        rows    = ALL_ROUNDS.get(sector,
            ALL_ROUNDS["Information Technology"])
        fc = [{"round":r,"sa":rows[r-1][1],"sb":rows[r-1][4],
               "chart_a":get_chart_url(sector,r,'A'),
               "chart_b":get_chart_url(sector,r,'B')}
              for r in range(1,6)]
        return render_template('survey_feedback.html',
            phase=1,summary=summary,start_r=1,end_r=5,
            sector=sector,feedback_charts=fc,
            condition=condition,
            goal=session.get('investment_goal',''),
            risk=session.get('risk_tolerance',''),
            hold=session.get('hold_duration',''))

    elif step == 'feedback_2':
        summary = calc_feedback(rd,6,10,sector)
        rows    = ALL_ROUNDS.get(sector,
            ALL_ROUNDS["Information Technology"])
        fc = [{"round":r,"sa":rows[r-1][1],"sb":rows[r-1][4],
               "chart_a":get_chart_url(sector,r,'A'),
               "chart_b":get_chart_url(sector,r,'B')}
              for r in range(6,11)]
        return render_template('survey_feedback.html',
            phase=2,summary=summary,start_r=6,end_r=10,
            sector=sector,feedback_charts=fc,
            condition=condition,
            goal=session.get('investment_goal',''),
            risk=session.get('risk_tolerance',''),
            hold=session.get('hold_duration',''))

    elif step == 'final_results':
        results = calc_final(sector,rd)
        session['final_results'] = results
        return render_template('survey_final.html',results=results)

    elif step == 'post_survey':
        return render_template('survey_post.html')

    elif step == 'thankyou':
        resp = make_response(render_template('survey_thankyou.html',
            pid=session.get('prolific_id','')))
        resp.set_cookie('study_completed','true',
                        max_age=60*60*24*365,httponly=True)
        return resp

    return redirect('/')

# ── ADMIN ─────────────────────────────────────────────────────────────────────
@app.route('/admin')
def admin():
    pw=request.args.get('pw','')
    if pw!='raj_admin_2024': return render_template('admin_login.html')
    rows=get_all_responses(); total=len(rows)
    ocis=[]; cond_a=0; cond_b=0
    for r in rows:
        try: ocis.append(float(r.get('oci',0)))
        except: pass
        if r.get('condition')=='A': cond_a+=1
        else: cond_b+=1
    avg_oci=round(sum(ocis)/len(ocis),1) if ocis else 0
    return render_template('admin.html',
        total=total,responses=rows[:20],
        avg_oci=avg_oci,cond_a=cond_a,cond_b=cond_b)

@app.route('/data')
def download_data():
    pw=request.args.get('pw','')
    if pw!='raj_data_conditionA_2024': return "Access denied",403
    rows=get_all_responses()
    if not rows: return "No data yet",404
    output=io.StringIO()
    writer=csv.DictWriter(output,fieldnames=ALL_FIELDS,extrasaction='ignore')
    writer.writeheader(); writer.writerows(rows)
    return output.getvalue(),200,{
        'Content-Type':'text/csv',
        'Content-Disposition':'attachment; filename=responses_AB.csv'}

@app.route('/ping')
def ping(): return 'alive',200

generate_all_charts()

if __name__=='__main__':
    init_db()
    app.run(debug=True,port=5000)
