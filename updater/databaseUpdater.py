import re
import json
import urllib.request
import logging
from babel import Locale
from pathlib import Path
from dataclasses import dataclass
from PySide6.QtCore import QObject, Signal

from properties.config import cfg
from scraping.utils import (
	itemsID, charactersID, weaponsID,
	echoesID, achievementsID, echoStats,
	definedText, sonataName
)

logger = logging.getLogger('DatabaseManager')

@dataclass
class FileConfig:
	folder: list[str]
	file: str

class DataUpdater(QObject):
	updateProgress = Signal(int, str)
	updateFinished = Signal()

	API = 'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
	NANOKA = 'https://static.nanoka.cc'

	def __init__(self):
		super().__init__()
		self.author = 'Dimbreath'
		self.repo = 'WutheringData'
		self.lang = self._getLanguage()
		self.files = [
			FileConfig(['TextMap', self.lang], 'MultiText.json'),
			FileConfig(['ConfigDB'], 'ItemInfo.json'),
			FileConfig(['ConfigDB'], 'WeaponConf.json'),
		]
		self.updated = False

	def _getLanguage(self) -> str:
		self.makeFolder()

		url = self.API.format(
			owner=self.author,
			repo=self.repo,
			path='TextMap'
		)
		uLang = cfg.get(cfg.gameLanguage)
		languages = self.loadJson('languages.json')
		
		if uLang not in languages:
			languages = {self._getLanguageName(item['name']): item['name'] for item in self.fetchFileData(url) if item['type'] == 'dir'}
			self.saveJson(languages, 'languages.json')

		return languages.get(uLang, 'en')

	def makeFolder(self):
		Path('data').mkdir(parents=True, exist_ok=True)
		logger.debug("Ensured 'data' directory exists.")

	def _getLanguageName(self, code: str) -> str:
		parts = code.split('-')
		locale = Locale(parts[0], script=parts[1] if len(parts) != 1 else None)
		try: return locale.get_display_name().capitalize()
		except: return code

	def fetchFileData(self, url: str) -> dict:
		try:
			with urllib.request.urlopen(urllib.request.Request(url)) as response:
				return json.loads(response.read().decode())
		except:
			return {}

	def updateFiles(self):
		for fileConfig in self.files:
			url = self.API.format(
				owner=self.author,
				repo=self.repo,
				path='/'.join(fileConfig.folder + [fileConfig.file])
			)

			logger.info(f'Checking for updates on file: {fileConfig.file}')
			try:
				data = self.fetchFileData(url)
				filePath: Path = Path('data') / fileConfig.file

				currentSize = filePath.stat().st_size if filePath.is_file() else 0

				if data['size'] != currentSize:
					logger.info(f'Downloading updated version of {fileConfig.file}...')
					urllib.request.urlretrieve(
						data['download_url'],
						filePath,
						reporthook=lambda block_num, block_size, total_size: self.reportProgress(fileConfig.file, block_num, block_size, total_size)
					)
					self.updated = True
					logger.info(f'File updated: {fileConfig.file}')
			except Exception as e:
				logger.error(f'Failed to update {fileConfig.file}. Error: {e}')
	
	
	def reportProgress(self, file_name, block_num, block_size, total_size):
		downloaded = block_num * block_size
		percent = (downloaded / total_size)*100
		self.updateProgress.emit(percent, file_name)

	def loadJson(self, filename: str) -> dict:
		try:
			with open(f'./data/{filename}', 'r', encoding='utf-8') as f:
				return json.load(f)
		except:
			return dict()

	def saveJson(self, data: dict, filename: str):
		with open(f'./data/{filename}', 'w', encoding='utf-8') as f:
			json.dump(data, f, indent=4)

	def updateItems(self):
		logger.info('Updating items.json...')
		try:
			infoText = self.loadJson('MultiText.json')
			itemInfo = self.loadJson('ItemInfo.json')
			weaponInfo = self.loadJson('WeaponConf.json')

			items = {
				infoText[item['Name']].lower().replace(' ', ''): {
					'id': item['Id'],
					'name': infoText[item['Name']],
					'image': item['Icon'].split('/Image/')[1].rsplit('.', 1)[0] + '.png'
				}
				for item in itemInfo if item['Name'] in infoText
			}
			weapons = {
				infoText[weapon['WeaponName']].lower().replace(' ', ''): {
					'id': weapon['ModelId'],
					'name': infoText[weapon['WeaponName']],
					'rarity': weapon['QualityId'],
					'image': weapon['Icon'].split('/Image/')[1].rsplit('.', 1)[0] + '.png'
				}
				for weapon in weaponInfo if weapon['WeaponName'] in infoText
			}

			self.saveJson(items, 'items.json')
			self.saveJson(weapons, 'weapons.json')

			itemsID.update(items)
			weaponsID.update(weapons)

		except Exception as e:
			logger.error(f'Failed to update items.json. Error: {e}', exc_info=True)

	def updateJsonFromPattern(self, fileName: str, pattern: str, transformFunc):
		logger.info(f'Updating {fileName}...')
		try:
			infoText = self.loadJson('MultiText.json')
			
			data = {}
			compiledPattern = re.compile(pattern)
			for key in infoText:
				if match := compiledPattern.match(key):
					transformed = transformFunc(infoText[key], match)
					if transformed is not None:
						data[transformed] = int(match.group(1))

			self.saveJson(data, fileName)
			return data
		except Exception as e:
			logger.error(f'Failed to update {fileName}. Error: {e}', exc_info=True)

	def updateCharacters(self):
		data = self.updateJsonFromPattern(
			'characters.json',
			r'^RoleInfo_(\d+)_Name$',
			lambda text, match: text.lower().replace(' ', '') if int(match.group(1)) < 5000 else None
		)
		if data:
			charactersID.update(data)

	def updateEcho(self):
		data = self.updateJsonFromPattern(
			'echoes.json',
			r'^MonsterInfo_(\d+)_Name$',
			lambda text, match: text.lower().replace(' ', '') if int(match.group(1)) < 350000000 else None
		)
		if data:
			echoesID.update(data)

	def updateAchievements(self):
		data = self.updateJsonFromPattern(
			'achievements.json',
			r'^Achievement_(\d+)_Name$',
			lambda text, _: text
		)
		if data:
			achievementsID.update(data)

	def updateEchoStats(self):
		statsKey = {
			'PropertyIndex_10003_Name': 'hp',
			'PropertyIndex_10007_Name': 'atk',
			'PropertyIndex_10008_Name': 'cr',
			'PropertyIndex_10009_Name': 'cd',
			'PropertyIndex_10010_Name': 'def',
			'PropertyIndex_10011_Name': 'er',
			'PropertyIndex_10014_Name': 'skillDmg',
			'PropertyIndex_10017_Name': 'basicAttack',
			'PropertyIndex_10018_Name': 'heavyAttack',
			'PropertyIndex_10019_Name': 'liberationDmg',
			'PropertyIndex_10022_Name': 'glacio',
			'PropertyIndex_10023_Name': 'fusion',
			'PropertyIndex_10024_Name': 'electro',
			'PropertyIndex_10025_Name': 'aero',
			'PropertyIndex_10026_Name': 'spectro',
			'PropertyIndex_10027_Name': 'havoc',
			'PropertyIndex_10035_Name': 'healing'
		}

		try:
			infoText = self.loadJson('MultiText.json')
			
			stats = {infoText[key].lower().replace(' ', '').replace('.', ''): value
					 for key, value in statsKey.items()}
			
			self.saveJson(stats, 'echoStats.json')
			echoStats.update(stats)
			
		except Exception as e:
			logger.error(f'Failed to update echoStats. Error: {e}', exc_info=True)

	def updateSonata(self):
		data = self.updateJsonFromPattern(
			'sonataName.json',
			r'^PhantomFetter_(\d+)_Name$',
			lambda text, _: text.lower().replace(' ', '')
		)
		if data:
			sonataName.extend(list(data))

	def updateDefinedText(self):
		textKey = [
			'PrefabTextItem_1547656443_Text',  # Terminal
			'PrefabTextItem_128820487_Text',   # Claim
			'PrefabTextItem_3963945691_Text'   # Activated
		]

		try:
			infoText = self.loadJson('MultiText.json')
			
			stats = {key: infoText[key].lower().replace(' ', '').replace('-', '').strip()
					 for key in textKey}
			
			self.saveJson(stats, 'definedText.json')
			definedText.update(stats)
			
		except Exception as e:
			logger.error(f'Failed to update definedText. Error: {e}', exc_info=True)

	def _nanokaLang(self) -> str:
		lang = self.lang.split('-')[0]
		if lang in ('en', 'ja', 'ko'):
			return lang
		return 'zh' if self.lang.startswith('zh') else 'en'

	def updateFromNanoka(self, force: bool = False):
		"""Rebuild characters.json and weapons.json from the maintained
		nanoka.cc (formerly hakush.in) dataset. The WutheringData repo the
		other tables come from stopped updating at game version 3.1, so it
		is missing every resonator and weapon released since."""
		try:
			with urllib.request.urlopen(f'{self.NANOKA}/manifest.json', timeout=15) as response:
				manifest = json.loads(response.read().decode())
			version = str(manifest.get('ww', {}).get('latest', '')).split('+')[0]
			if not version:
				return

			cached = self.loadJson('nanokaVersion.json').get('version')
			if not force and cached == version \
					and (Path('data') / 'characters.json').is_file() \
					and (Path('data') / 'weapons.json').is_file():
				return

			lang = self._nanokaLang()

			def fetchTable(table: str) -> dict:
				with urllib.request.urlopen(f'{self.NANOKA}/ww/{version}/{table}.json', timeout=30) as response:
					return json.loads(response.read().decode())

			characters = {}
			for charID, info in fetchTable('character').items():
				name = str(info.get(lang) or info.get('en') or '')
				if name:
					characters[name.lower().replace(' ', '')] = int(charID)
			if characters:
				self.saveJson(characters, 'characters.json')
				charactersID.update(characters)

			weapons = {}
			for weaponID, info in fetchTable('weapon').items():
				name = str(info.get(lang) or info.get('en') or '')
				if not name:
					continue
				icon = str(info.get('icon', ''))
				image = icon.split('/Image/')[1].rsplit('.', 1)[0] + '.png' if '/Image/' in icon else ''
				weapons[name.lower().replace(' ', '')] = {
					'id': int(weaponID),
					'name': name,
					'rarity': info.get('rank', 1),
					'image': image
				}
			if weapons:
				self.saveJson(weapons, 'weapons.json')
				weaponsID.update(weapons)

			self.saveJson({'version': version}, 'nanokaVersion.json')
			logger.info(f'Updated characters/weapons from nanoka.cc (ww {version}, {lang})')
		except Exception as e:
			logger.error(f'Failed to update from nanoka.cc: {e}', exc_info=True)

	def run(self):
		self.updateFiles()
		derivedFiles = (
			'items.json', 'weapons.json', 'echoStats.json', 'sonataName.json',
			'definedText.json', 'achievements.json', 'characters.json', 'echoes.json'
		)
		derivedMissing = any(not (Path('data') / f).is_file() for f in derivedFiles)
		if self.updated or derivedMissing:
			self.updateItems()
			self.updateEchoStats()
			self.updateSonata()
			self.updateDefinedText()
			self.updateAchievements()
			self.updateCharacters()
			self.updateEcho()
		self.updateFromNanoka(force=self.updated or derivedMissing)
		self.updateFinished.emit()