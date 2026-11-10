from pathlib import Path
import datetime as dt
import importlib.util
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
spec=importlib.util.spec_from_file_location('axr_stats',ROOT/'src/axr_stats.py')
axr=importlib.util.module_from_spec(spec);spec.loader.exec_module(axr)

class TestAXRStats(unittest.TestCase):
    def setUp(self):
        self.lifetime={'data':{'total_seconds':145*3600}}
        self.month={'data':{'total_seconds':10000,'languages':[{'name':'TypeScript','total_seconds':7000}]}}
        self.week={'data':{'total_seconds':3600}}
        self.today=dt.date(2026,11,10)
        self.summaries={'data':[{'range':{'date':'2026-11-10'},'grand_total':{'total_seconds':7200}}]}

    def test_all_cards_render_as_valid_svg(self):
        for theme in axr.THEMES:
            result=axr.cards(self.lifetime,self.month,self.week,self.summaries,{},self.today,theme)
            self.assertEqual(len(result),6)
            for name,svg in result.items():
                self.assertEqual(ET.fromstring(svg).tag,'{http://www.w3.org/2000/svg}svg',name)
                self.assertNotIn('Card Error',svg)
            self.assertIn('Artisan',result['lifetime.svg'])
            self.assertIn('Position not confirmed',result['ranking.svg'])

    def test_official_rank_only_when_numeric(self):
        valid=axr.cards(self.lifetime,self.month,self.week,self.summaries,{'current_user':{'rank':8937}},self.today)
        self.assertIn('#8937',valid['ranking.svg'])
        invalid=axr.cards(self.lifetime,self.month,self.week,self.summaries,{'current_user':{'rank':'8937'}},self.today)
        self.assertNotIn('#8937',invalid['ranking.svg'])

    def test_levels(self):
        self.assertEqual(axr.level_for(0)[1],'Novice')
        self.assertEqual(axr.level_for(145)[1],'Artisan')
        self.assertEqual(axr.level_for(2600)[1],'Legend')

    def test_xml_escaping(self):
        self.month['data']['languages'][0]['name']='<script onload="danger">'
        svg=axr.cards(self.lifetime,self.month,self.week,self.summaries,{},self.today)['languages.svg']
        self.assertNotIn('<script',svg)
        self.assertIn('&lt;script',svg)
        ET.fromstring(svg)

    def test_invalid_stats_and_no_token(self):
        with self.assertRaises(RuntimeError):
            axr.cards({'data':{}},self.month,self.week,self.summaries,{},self.today)
        with self.assertRaises(RuntimeError):
            axr.cards(self.lifetime,{'data':[]},self.week,self.summaries,{},self.today)

    def test_output_files(self):
        result=axr.cards(self.lifetime,self.month,self.week,self.summaries,{},self.today)
        with tempfile.TemporaryDirectory() as tmp:
            axr.write_cards(result,tmp)
            self.assertEqual(len(list(Path(tmp).glob('*.svg'))),6)
            self.assertIn('Artisan',(Path(tmp)/'lifetime.svg').read_text(encoding='utf-8'))

if __name__=='__main__': unittest.main()

    def test_all_time_language_stats_are_not_30_day_stats(self):
        historical={'data':{'total_seconds':3600*121,'languages':[{'name':'Rust','total_seconds':3600*110}]}}
        result=axr.cards(self.lifetime,self.month,self.week,self.summaries,{},self.today,all_langs=historical)
        self.assertIn('All-time coding languages',result['languages.svg'])
        self.assertIn('Rust',result['languages.svg'])
        self.assertNotIn('TypeScript',result['languages.svg'])
        self.assertIn('121h',result['languages.svg'])

    def test_embedded_rank_art_and_individual_svgs(self):
        from rank_art import rank_svg,standalone
        elements=[]
        for index in range(7):
            image=standalone(index)
            ET.fromstring(image)
            self.assertIn('linearGradient',image)
            elements.append(image)
        self.assertEqual(len(set(elements)),7)
        self.assertIn('linearGradient',axr.cards(self.lifetime,self.month,self.week,self.summaries,{},self.today)['lifetime.svg'])

    def test_activity_text_is_separated_from_gauge(self):
        card=axr.activity_card(3600,1800,axr.THEMES['midnight'])
        self.assertIn('Logged today',card)
        self.assertIn('M81 206',card)
        ET.fromstring(card)
