"""
Prompt pull/first rider in front and list next pulls, during team race using a pace line.
"""
import logging
import argparse
import os
import sys
from configparser import ConfigParser


class PaceLine(object):

    def __init__(self, rider_list, sort_by_name=True, min_num_rider=4):
        assert isinstance(rider_list, list)
        assert rider_list
        assert isinstance(sort_by_name, bool)
        assert isinstance(min_num_rider, int), min_num_rider
        assert len(rider_list) == len(set(rider_list)), 'riders are not unique'
        if sort_by_name:
            rider_list = sorted(rider_list)
        self._rider_list = rider_list.copy()
        self._min_num_rider = min_num_rider

    def run(self):
        self._wait_for_start()
        curr_pull_idx = 0
        rider_idx = 0
        action = input(self._prompt_pull_rider(rider_idx))
        while action != 'D':
            action = 'Y' if action == '' else action.upper()
            if action == 'S':
                logging.info(f'--> Skip rider {self._get_rider_name(rider_idx)}')
                rider_idx += 1
            elif action == 'Q':
                logging.info(f'--> {self._get_rider_name(rider_idx)} quit the race :(')
                self._rider_list.pop(rider_idx % len(self._rider_list))
                assert len(self._rider_list) >= self._min_num_rider, \
                        f'Only {len(self._rider_list)} riders left! {self._rider_list}'
                logging.info(f'{len(self._rider_list)} riders left: {self._rider_list}')
            elif action.upper() == 'Y':
                logging.info(f'--> Confirmed!')
                logging.info(f'Pull number {curr_pull_idx + 1}: {self._get_rider_name(rider_idx)}')
                curr_pull_idx += 1
                rider_idx += 1
            else:
                logging.info(f'--> Taking a break...')
            action = input(self._prompt_pull_rider(rider_idx))
        logging.info(f'Race is done!')

    def _prompt_pull_rider(self, rider_idx):
        return (f'--> Next pull: {self._get_rider_list(rider_idx)}\n'
                f'[Y] to confirm, S to skip, Q for this rider to quit, D if the race is done:\n')

    def _get_rider_name(self, rider_idx):
        return self._rider_list[rider_idx % len(self._rider_list)]

    def _get_rider_list(self, start_idx):
        rider_list = []
        num_rider = len(self._rider_list)
        for i in range(num_rider):
            rider_list.append(self._rider_list[(start_idx + i) % num_rider])
        return rider_list

    def _wait_for_start(self):
        ready_to_start = False
        while not ready_to_start:
            logging.info('Not ready to start')
            key_input = input('--> Ready to Start? [Y]')
            logging.info(f'get "{key_input}"')
            ready_to_start = key_input == '' or key_input.upper() == 'Y'
        logging.info(f'--> Start pace line')


def mkdir_p(dir_path):
    assert isinstance(dir_path, str), dir_path
    if dir_path == '':
        return
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        return
    try:
        os.makedirs(dir_path)
    except Exception:
        f'makedirs({dir_path}) failed'
        raise
    assert os.path.isdir(dir_path), f'{dir_path} is not a directory'


def create_parser():
    parser = argparse.ArgumentParser(description="Pace line prompter",
                                     prog='pace_line',
                                     prefix_chars='-',
                                     fromfile_prefix_chars='@',
                                     conflict_handler='resolve',
                                     add_help=True,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--config_file", required=True,
                        help="config file including all the input and paramter specifications")
    parser.add_argument("--log_file", required=False, default='',
                        help="log file in addition to screen log")
    return parser


def set_up_logger(log_file):
    # TODO: set up file logger with specified log file name, and blackhole logger

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(lineno)d: %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file:
        mkdir_p(os.path.dirname(log_file))
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


def main():

    parser = create_parser()
    args = parser.parse_args()
    config_file = args.config_file
    log_file = args.log_file
    assert os.path.isfile(config_file), f'{config_file} does not exist'
    set_up_logger(log_file)

    config = ConfigParser()
    config.read(config_file)
    assert isinstance(config, ConfigParser), type(config)
    rider_list = [rider.strip() for rider in config.get('DEFAULT', 'riders').split(',')]
    logging.info(f'rider_list: {rider_list}, log_file={log_file}')
    PaceLine(rider_list).run()


if __name__ == '__main__':
    sys.exit(main())
