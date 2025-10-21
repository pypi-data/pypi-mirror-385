import pprint
import requests
from DIRAC import S_OK, S_ERROR, gConfig
from DIRAC.Core.Base.AgentModule import AgentModule
from DIRAC.WorkloadManagementSystem.Client import JobStatus
from DIRAC.WorkloadManagementSystem.DB.JobDB import JobDB
from DIRAC.ConfigurationSystem.Client.Helpers.Operations import Operations
from DIRAC.Core.Utilities.ObjectLoader import ObjectLoader
from DIRAC.ConfigurationSystem.Client.Helpers import Registry
from DIRAC.ConfigurationSystem.Client import PathFinder


JOB_PARAMETER_KEYS = ["ModelName",
            "CPUNormalizationFactor",
            "HostName",
            "JobID",
            "JobType",
            "LoadAverage",
            "MemoryUsed(kb)",
            "NormCPUTime(s)",
            "ScaledCPUTime(s)",
            "Status",
            "TotalCPUTime(s)",
            "WallClockTime(s)",
            "DiskSpace(MB)",
            "CEQueue",
            "GridCE",
       ]

JOB_ATTRIBUTE_KEYS = [
                       "JobGroup",
                       "JobName",
                       "Owner",
                       "OwnerDN",
                       "OwnerGroup",
                       "RescheduleCounter",
                       "Site",
                       "SubmissionTime",
                       "StartExecTime",
                       "EndExecTime",
                       "SystemPriority",
                       "UserPriority",
                     ]

TIME_STAMPS = [
                "SubmissionTime",
                "StartExecTime",
                "EndExecTime",
]

# Some tentative values
DEFAULT_CI = 24
DEFAULT_PUE = 1.5
DEFAULT_TDP = 150

# Getting tokens at

METRICS_DB_URL = "https://mc-a4.lab.uvalight.net/gd-cim-api/submit"
METRICS_DB_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhdHNhcmVnQGluMnAzLmZyIiwiaXNzIjoiZ3JlZW5kaWdpdC1sb2dpbi11dmEiLCJpYXQiOjE3NTkzMDA5ODYsIm5iZiI6MTc1OTMwMDk4NiwiZXhwIjoxNzU5Mzg3Mzg2fQ.A4nygJEdhvOQjkLe-ckRDidqVbi6-s4kZXLRUZkwek8"


class GreenReportingAgent(AgentModule):
    """
    Agent for removing jobs in status "Deleted", and not only
    """

    def __init__(self, *args, **kwargs):
        """c'tor"""
        super().__init__(*args, **kwargs)

        # clients
        self.jobDB = None

        self.maxJobsAtOnce = 50
        self.section = PathFinder.getAgentSection(self.agentName)

    #############################################################################
    def initialize(self):
        """Sets defaults"""

        self.jobDB = JobDB()
        self.elasticJobParametersDB = None
        useESForJobParametersFlag = Operations().getValue("/Services/JobMonitoring/useESForJobParametersFlag", False)
        if useESForJobParametersFlag:
            try:
                result = ObjectLoader().loadObject(
                    "WorkloadManagementSystem.DB.ElasticJobParametersDB", "ElasticJobParametersDB"
                )
                if not result["OK"]:
                    return result
                self.elasticJobParametersDB = result["Value"](parentLogger=self.log)
            except RuntimeError as excp:
                return S_ERROR(f"Can't connect to ES DB: {excp}")

        self.maxJobsAtOnce = self.am_getOption("MaxJobsAtOnce", self.maxJobsAtOnce)

        self.cpuDict = {}
        result = gConfig.getSections(f"{self.section}/CPUData")
        if result["OK"]:
            models = result["Value"]
            for model in models:
                self.cpuDict[model] = {}
                self.cpuDict[model]["TDP"] = gConfig.getValue(f"{self.section}/CPUData/{model}/TDP", DEFAULT_TDP)
                self.cpuDict[model]["Cores"] = gConfig.getValue(f"{self.section}/CPUData/{model}/Cores", 12)

        print("AT >>> CPU data")
        pprint.pprint(self.cpuDict)

        return S_OK()

    def execute(self):
        """Report job green parameters"""

        condDict = {"Status": [JobStatus.DONE, JobStatus.FAILED], "ApplicationNumStatus": 0}
        result = self.jobDB.selectJobs(condDict, limit=self.maxJobsAtOnce, orderAttribute="LastUpdateTime:DESC" )
        if not result["OK"]:
            return result

        jobList = result["Value"]
        if not jobList:
            self.log.info("No jobs to report")
            return S_OK()

        print("Job List", jobList)

        result = self.elasticJobParametersDB.getJobParameters(jobList)
        if not result["OK"]:
            self.log.info("No parameters found")
            return S_ERROR("No parameters found")
        jobParamsDict = result["Value"]

        result = self.jobDB.getJobsAttributes(jobList)
        if not result["OK"]:
            self.log.info("No attributes found")
            return S_ERROR("No attributes found")
        jobAttrDict = result["Value"]


        #pprint.pprint(jo)
        #pprint.pprint(jobAttrDict)
        print("hello world")
        # Form records
        records = []
        for job in jobParamsDict:
            jobDict = {}
            for key in jobParamsDict[job]:
                if key in JOB_PARAMETER_KEYS:
                    jobDict[key] = jobParamsDict[job][key]
            for key in jobAttrDict[job]:
                if key in JOB_ATTRIBUTE_KEYS:
                    if key in TIME_STAMPS:
                       jobDict[key] = str(jobAttrDict[job][key])
                    else:
                       jobDict[key] = jobAttrDict[job][key]

            records.append(jobDict)

        # Mark jobs as reported
        result = self.jobDB.setJobAttributes(jobList, ["ApplicationNumStatus"], [9999])
        if not result["OK"]:
            self.log.error(f"Failed to set ApplicationNumStatus for job {job}", result["Message"])

        #for record in records:
        #    pprint.pprint(record)

        # Get the processor TDP
        for record in records:
            result = self.__getProcessorParameters(record.get("ModelName", "Unknown"))
            if not result["OK"]:
                self.log.error("Failed to get processor parameters")
                continue
            tdp, n_cores = result["Value"]
            site = record.get("Site", "Unknown")
            result = self.__getSiteParameters(record["Site"])
            if not result["OK"]:
                self.log.error("Failed to get site parameters")
                continue
            pue, ci, gocdb_name = result["Value"]
            cpu = record.get("TotalCPUTime(s)", 0)
            cpu = float(cpu)
            record["Energy(kwh)"] = cpu*tdp/n_cores/1000./3600.
            record["TDP"] = tdp
            record["NCores"] = n_cores
            record["VO"] = Registry.getVOForGroup(record["OwnerGroup"])
            record["SiteName"] = gocdb_name

        for record in records:
            pprint.pprint(record)
            result = self.__sendRecordToMB(record)

        # Send records to the Metrics DB

        return S_OK()

    def __sendRecordToMB(self, record):

        headers = { "Authorization": f"Bearer {METRICS_DB_TOKEN}",
                    "Content-Type": "application/json"
                  }

        response = requests.post(METRICS_DB_URL,
                                 headers = headers,
                                 json = record
                                )
        print(response.status_code)
        print(response.text)

        return S_OK()

    def __getSiteParameters(self, site):
        """ To be implemented """

        grid = site.split(".")[0]
        gocdb_name = gConfig.getValue(f"/Resources/Sites/{grid}/{site}/Name", site)
        pue = gConfig.getValue(f"/Resources/Sites/{grid}/{site}/GreenParams/PUE", DEFAULT_PUE)
        ci = gConfig.getValue(f"/Resources/Sites/{grid}/{site}/GreenParams/CI", DEFAULT_CI)
        return S_OK((pue, ci, gocdb_name))

    def __getProcessorParameters(self, model):
        """ Get TDP and number of cores """

        if model in self.cpuDict:
            return S_OK((self.cpuDict[model]["TDP"], self.cpuDict[model]["Cores"]))

        print(f"AT >>> oooooooooooooo CPU Model {model} is not in the configuration ooooooooooooooo")
        return S_OK((200, 12))