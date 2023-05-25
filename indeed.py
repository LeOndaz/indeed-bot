import argparse

from scrapers.indeed_eg import IndeedEGAutomationProcedure
from scrapers.indeed_us import IndeedUSAutomationProcedure
from utils import setup_webdriver

if __name__ == "__main__":
    import asyncio

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--region", "-r", metavar="region", dest="region")
    arg_parser.add_argument("--email", "-e", metavar="email", dest="email")
    arg_parser.add_argument("--pwd", "-p", metavar="password", dest="password")
    arg_parser.add_argument("--what", "-wt", metavar="what", dest="what")
    arg_parser.add_argument("--where", "-wr", metavar="where", dest="where")
    args = arg_parser.parse_args()

    assert all(
        [args.region, args.email, args.password, args.what, args.where]
    ), "You didn't provide all the necessary fields."

    def start_as_script():
        driver = setup_webdriver()

        if args.region == "us":
            procedure = IndeedUSAutomationProcedure(driver)
        elif args.region == "eg":
            procedure = IndeedEGAutomationProcedure(driver)
        else:
            raise ValueError("indeed automation supports currently us/eg regions only.")

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            procedure.start(
                args.email,
                args.password,
                args.what,
                args.where,
                lambda: input("Enter the code you'll receive on your mail shortly: "),
            )
        )

    start_as_script()
