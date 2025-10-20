from typing import TYPE_CHECKING, Optional
from Hql.Exceptions import HacExceptions as hace
from Hql.Exceptions import HqlExceptions as hqle
from Hql.Compiler import InstructionSet
from pathlib import Path
import datetime
import logging
import time

from Hql.Helpers import can_thread

if TYPE_CHECKING:
    from Hql.Config import Config
    from Hql.Hac import Hac
    from Hql.Parser import SigmaParser
    from Hql.Data import Data
    from Hql.Compiler import HqlCompiler

class CronException(Exception):
    def __init__(self, message:str=""):
        self.type = self.__class__.__name__
        Exception.__init__(self, f"Invalid cron schedule {message}")

class Schedule():
    def __init__(self, cronstr:str) -> None:
        self.cronstr = cronstr
        self.last_fired = 0
        self.weekdays = ['sun', 'mon', 'tues', 'wed', 'thu', 'fri', 'sat']
        self.bounds = {
            'minutes':  (0, 59),
            'hours':    (0, 23),
            'days':     (1, 31),
            'months':   (1, 12),
            'weekdays': (0, 6)
        }
        self.schedule:tuple[set, set, set, set, set] = self.parse_cron(cronstr)

    def should_fire(self, time_parts:tuple[int, int, int, int, int]):
        for i in range(5):
            if time_parts[i] not in self.schedule[i]:
                return False
        return True

    def parse_cron(self, cronstr:str) -> tuple[set, set, set, set, set]:
        parts = cronstr.split(' ')

        for p in parts:
            if not p:
                parts.remove(p)
        
        minutes = self.parse_part(parts[0], 'minutes')
        hours = self.parse_part(parts[1], 'hours')
        months = self.parse_part(parts[2], 'months')
        days = self.parse_part(parts[3], 'days')
        weekdays = self.parse_part(parts[4], 'weekdays')

        return (minutes, hours, months, days, weekdays)

    def parse_part(self, part:str, kind:str) -> set[int]:
        out_set:set[int] = set()
        opts = part.split(',')

        for i in opts:
            interval = 0
            value = i
            if len(i.split('/')) > 1:
                interval = i.split('/')[1]
                value = i.split('/')[0]

                try:
                    interval = int(interval)
                except ValueError:
                    raise CronException(f'Invalid cron schedule {self.cronstr}')
            
            start = value
            end = ''
            if len(start.split('-')) > 1:
                end = start.split('-')[1]
                start = start.split('-')[0]

            if end and ('*' in start or '*' in end):
                raise CronException(f'Invalid cron schedule {self.cronstr}')

            if kind == 'weekdays':
                if start in self.weekdays:
                    start = self.weekdays.index(start)
                if end in self.weekdays:
                    end = self.weekdays.index(end)

            try:
                if not isinstance(start, int) and start != '*':
                    start = int(start)
                if end and not isinstance(end, int):
                    end = int(end)
            except ValueError:
                raise Exception(f'Invalid cron schedule {self.cronstr}')

            bot, top = self.bounds[kind]
            if not end and interval:
                end = top

            if start != '*':
                if (start < bot or start > top):
                    raise CronException(self.cronstr)

                if end and (end < start or end < bot or end > top):
                    raise CronException(self.cronstr)

            if not interval:
                if start == '*':
                    [out_set.add(x) for x in range(bot, top + 1)]
                elif end:
                    [out_set.add(x) for x in range(start, end + 1)]
                else:
                    out_set.add(start)

            else:
                assert start != '*'
                if end:
                    [out_set.add(x) for x in range(start, end + 1, interval)]
                else:
                    [out_set.add(x) for x in range(start, top + 1, interval)]

        return out_set

class Detection():
    def __init__(self, txt:str, src:str, config:'Config', no_hac:bool=False) -> None:
        import uuid

        self.src = src
        self.txt = txt
        self.config = config
        self.hac, self.parser = self.gen_hac()
        self.compiler:Optional['HqlCompiler'] = None
        self.schedule:Optional[Schedule] = None
        self.id = ''
        
        self.run_history:list[dict] = []
        self.max_runs = 10

        # skip instruction compiling if we don't have hac
        if self.hac:
            self.id = self.hac.id
            self.compiler = self.compile()

            # Just don't schedule if not a hac run
            if not no_hac:
                self.schedule = Schedule(self.hac.schedule)

        elif no_hac:
            self.id = str(uuid.uuid4())
            self.compiler = self.compile()

    def to_dict(self) -> dict:
        res = {
            'id': self.id,
            'hql': self.txt,
            'history': self.run_history
        }

        if self.schedule:
            res['schedule'] = self.schedule.cronstr

        return res

    def gen_hac(self) -> tuple[Optional['Hac'], Optional['SigmaParser']]:
        from Hql.Hac import Parser as HaCParser
        from Hql.Parser import SigmaParser

        parser = None
        hac = None

        try:
            parser = SigmaParser(self.txt)
            hac = parser.gen_hac()
        except Exception:
            # We're just skipping over to HaC Parsing then
            try:
                hac = HaCParser.parse_text(self.txt, self.src)
            except (hace.LexerException, hace.HacException):
                hac = None

        return hac, parser

    def deparse(self) -> str:
        from Hql.Query import Query
        from Hql.Context import Context
        from Hql.Data import Data

        deparse = ''

        if self.hac:
            deparse += self.hac.render(target='decompile')
            deparse += '\n'

        if not self.parser:
            raise hqle.CompilerException(f'Attempting to deparse an unparsed query {self.id}')
        
        if not isinstance(self.parser.assembly, Query):
            raise hqle.CompilerException(f'Attempting to compile non-Query assembly {type(self.parser.assembly)}')

        deparse += self.parser.assembly.decompile(Context(Data()))
        
        return deparse

    def compile(self) -> 'HqlCompiler':
        from Hql.Parser import Parser
        from Hql.Query import Query
        from Hql.Compiler import HqlCompiler

        logging.debug(f'Compiling {self.src}')

        if not self.parser:
            self.parser = Parser(self.txt, self.src)
        self.parser.assemble()
    
        if not isinstance(self.parser.assembly, Query):
            raise hqle.CompilerException(f'Attempting to compile non-Query assembly {type(self.parser.assembly)}')

        comp = HqlCompiler(self.config, query=self.parser.assembly, hac=self.hac)
        return comp

    def should_fire(self, time_parts:tuple[int, int, int, int, int]):
        if not self.schedule:
            return False
        return self.schedule.should_fire(time_parts)

    def add_run(self, run:dict):
        if len(self.run_history) >= 10:
            diff = len(self.run_history) - 9
            self.run_history = self.run_history[diff:]
        self.run_history.append(run)

    def run(self) -> 'Data':
        if not self.compiler:
            raise Exception('Attempting to run detection without instructions!')
        
        start = time.perf_counter()
        ctx = self.compiler.run()
        end = time.perf_counter()

        run = {
            'id': self.id,
            'duration': end - start,
            'results': len(ctx.data)
        }
        self.add_run(run)

        return ctx.data

class HacEngine():
    def __init__(self, path:Path, directory:bool, conf_path:Path, tz:Optional[datetime.tzinfo]=None) -> None:
        from Hql.Threading import HacPool, HacThread
        from Hql.Apiserver import Apiserver

        self.path = path
        self.directory = directory
        self.files:list[Path] = self.scan_files()
        self.conf_path = conf_path
        self.config = self.load_conf()
        self.detections:dict[str, Detection] = self.load_files()
        self.tz = tz

        if can_thread():
            self.apiserver = Apiserver(self)
        else:
            self.apiserver = None

        self.pool = HacPool()
        self.completed:list[HacThread] = []
        self.clean_time = datetime.timedelta(days=1)

    def time_parts(self, ts:int) -> tuple[int, int, int, int, int]:
        dt = datetime.datetime.fromtimestamp(ts, tz=self.tz)
        return (dt.minute, dt.hour, dt.month, dt.day, dt.weekday())

    def load_conf(self):
        from Hql.Config import Config
        return Config(self.conf_path)

    def scan_files(self) -> list[Path]:
        files = []

        if self.directory:
            # Hql
            for file in self.path.rglob('*.hql'):
                if file.is_file():
                    files.append(file)
            # yml
            for file in self.path.rglob('*.yml'):
                if file.is_file():
                    files.append(file)
        else:
            files.append(self.path)

        return files

    def load_files(self) -> dict[str, Detection]:
        detections = dict()

        for i in self.files:
            with open(i, mode='r') as f:
                txt = f.read()    
            detection = Detection(txt, str(i), self.config)
            detections[detection.id] = detection

        logging.info(f'HaC engine found {len(detections)} detections')

        return detections

    def write_detection(self, text:str='', detection:Optional[Detection]=None):
        if text:
            detection = Detection(text, 'hac-engine', self.config)
        
        if detection == None:
            logging.error('Failed to generate detection from text')
            raise hqle.HqlException(f'Failed to parse hql detection')

        if self.directory:
            path = self.path / f'{detection.id}.hql'
        else:
            path = self.path

        with open(path, mode='w+') as f:
            f.write(detection.txt)

        return detection

    def wait_till(self, stamp:int, pad:int=0):
        from time import sleep
        cur = datetime.datetime.now(tz=self.tz).timestamp()
        if stamp <= cur:
            return
        delta = (stamp - cur) - pad
        sleep(delta)

    def clean_old(self):
        for t in self.completed:
            if (datetime.datetime.now() - t.run_date) > self.clean_time:
                logging.info(f'HaC thread {t.id} expired, cleaning')
                self.completed.remove(t)
                
    def get_by_id(self, tid:str):
        for i in self.completed:
            if i.id == tid:
                return i
        return self.pool.get_by_id(tid)

    def get_runs(self):
        runs = []
        for i in self.completed:
            runs.append({
                'run_id': i.id,
                'run_date': i.run_date.isoformat(),
                'started': i.started,
                'failed': i.failed,
                'completed': i.completed,
                'num_results': i.num_results
            })
        runs += self.pool.get_runs()
        return runs

    def run_detection(self, detection:Detection):
        return self.pool.add_detection(detection)

    def run(self):
        logging.info(f'Starting HaC engine with {len(self.detections)} detections')

        if self.apiserver:
            self.apiserver.start()

        while True:
            # adding 1 seconds for a time buffer
            dt = datetime.datetime.now(tz=self.tz) + datetime.timedelta(seconds=1)
            ts = dt.replace(second=0, microsecond=0) + datetime.timedelta(minutes=1)
            ts = int(ts.timestamp())
            self.wait_till(ts)

            for i in self.detections:
                det = self.detections[i]
                if not det.should_fire(self.time_parts(ts)):
                    logging.debug(f'Skipping {det.id}, not their time')
                    continue
                self.pool.add_detection(det)

            self.completed += self.pool.get_completed()
            self.clean_old()
