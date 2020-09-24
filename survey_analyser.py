# -*- coding: utf-8 -*-
#   Copyright 2020 Stanford University
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
"""
Created on Wed Feb 12 15:51:32 2020
@author: Hugo
"""

import os
import csv


def get_surveys(user_name, logger):
    """
    Used to parse survey answers file (in the "qualtrics_survey" folder).
    
    One "survey answer" is recorded when the user answers at least one question
    in the survey. One survey answer contains information about questions answers.
    The survey answers file contains one line per survey answer.
    The format of one line is something like that:
        start_date,...,% of completion,...,answer Q1,...,answer Qn,...,user_name
        
    This function returns all the lines that contain the given user_name.
    WARNING: At the moment, the only file format supported is CSV
    """
    
    logger.info("Searching survey answers for {}...".format(user_name))
    try:
        file_name = "qualtrics_survey/{}.{}".format(os.environ.get("SURVEY_NAME"), os.environ.get("FILE_FORMAT"))
        with open(file_name) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            
            answers = []
            for row in csv_reader:
                # Could be improve in retrieving dynamically the user_name index
                # ex: row[-1] => row["user_name"]
                if row[-1] == user_name:
                    answers.append(row)
        
        if answers:
            logger.info("{} answer(s) found for {}".format(len(answers), user_name))
            return answers
        else:
            logger.warning("No answer found for {}".format(user_name))
    except Exception as err:
        logger.excepion("Survey file not found:")


def get_last_survey(user_name, logger):
    """
    Starts by retrieving all survey answers of the given user.
    Filters the answers to keep only the ones with 100% completion.
    Returns the last survey answer
    """
    
    surveys = get_surveys(user_name, logger)
    
    try:
        # Can be improved in retrieving dynamically parameters of the survey
        # ex: survey[4] => survey["Progress"] or survey[1] => survey["EndDate"]
        if surveys:
            # Select only surveys with 100% completion
            surveys = [survey for survey in surveys if survey[4] == "100"]
            
            if surveys:
                # Sort surveys according to the time of completion
                surveys.sort(key=lambda x: x[1])
            
                return surveys[-1]
    except Exception as err:
        logger.exception("[ERROR] Survey answer parsing error:")