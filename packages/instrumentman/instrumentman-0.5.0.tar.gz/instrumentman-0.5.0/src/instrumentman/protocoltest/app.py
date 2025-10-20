from logging import Logger, getLogger
from typing import Any
from collections.abc import Callable

from rich.live import Live
from rich.table import Table, Column
from rich.prompt import Confirm
from geocompy.data import Angle
from geocompy.geo import GeoCom
from geocompy.geo.gcdata import Device
from geocompy.geo.gctypes import GeoComCode, GeoComResponse
from geocompy.gsi.dna import GsiOnlineDNA
from geocompy.gsi.gsitypes import GsiOnlineResponse
from geocompy.communication import open_serial

from ..utils import print_error, console


def _test_geocom_mot(tps: GeoCom) -> GeoComResponse[Any]:
    tps.mot.stop_controller()
    return tps.mot.start_controller()


def _test_geocom_ftr(tps: GeoCom) -> GeoComResponse[Any]:
    for device in Device:
        response = tps.ftr.setup_listing(device)
        tps.ftr.abort_listing()
        if response.error == GeoComCode.OK:
            return response

    return response


def tests_geocom(
    tps: GeoCom,
    logger: Logger
) -> None:
    console.print("GeoCOM connection successful")
    console.print(
        "Various GeoCOM functions will be tested. Certain settings will be "
        "changed on the instrument (ATR off, prism target off, etc.)."
    )
    console.print(
        "The program will attempt to use motorized functions. Give "
        "appropriate clearance for the instrument!"
    )
    Confirm.ask("Proceed with tests", console=console, default=True)

    logger.info("Starting GeoCOM tests")
    tests: list[
        tuple[str, Callable[..., GeoComResponse[Any]], tuple[Any, ...]]
    ] = [
        ("Alt User", tps.aus.switch_user_atr, (False,)),
        ("Automation", tps.aut.turn_to, (0, Angle(180, 'deg'))),
        ("Basic Applications", tps.bap.get_measurement_program, ()),
        ("Basic Man-Machine Interface", tps.bmm.beep_normal, ()),
        ("Camera", tps.cam.set_focus_to_infinity, ()),
        ("Central Services", tps.csv.get_instrument_name, ()),
        ("Control Task", tps.ctl.get_wakeup_counter, ()),
        ("Digital Level", tps.dna.switch_staffmode, (False,)),
        (
            "Electronic Distance Measurement",
            tps.edm.switch_laserpointer,
            (False,)
        ),
        ("File Transfer", _test_geocom_ftr, (tps,)),
        ("Imaging", tps.img.get_telescopic_configuration, ()),
        ("Keyboard Display Unit", tps.kdm.get_display_power_status, ()),
        ("Motorization", _test_geocom_mot, (tps,)),
        ("Supervisor", tps.sup.get_poweroff_configuration, ()),
        (
            "Theodolite Measurement and Calculation",
            tps.tmc.get_station,
            ()
        ),
        ("Word Index Registration", tps.wir.get_recording_format, ()),
    ]
    table = Table(
        "Subsystem",
        Column("Available", justify="center")
    )
    with Live(table, console=console):
        for subsystem, cmd, params in tests:
            response = cmd(*params)
            if response.error == GeoComCode.OK:
                result = ":white_check_mark:"
            else:
                result = ":x:"
                logger.error(f"{subsystem} unavailable ({response})")

            table.add_row(subsystem, result)

    logger.info("Tests complete")


def tests_gsidna(
    dna: GsiOnlineDNA,
    logger: Logger
) -> None:
    console.print("GSI Online connection successful")
    console.print(
        "Various GSI Online DNA functions will be tested. Certain settings "
        "might be changed on the instrument (staff mode, point number, etc.)."
    )
    Confirm.ask("Proceed with tests", console=console, default=True)

    logger.info("Starting GSI Online DNA tests")
    tests: list[
        tuple[str, Callable[..., GsiOnlineResponse[Any]], tuple[Any, ...]]
    ] = [
        ("Settings queries", dna.settings.get_staff_mode, ()),
        ("Settings commands", dna.settings.set_staff_mode, (False,)),
        (
            "Measurement/database queries",
            dna.measurements.get_point_id,
            ()
        ),
        (
            "Measurement/database commands",
            dna.measurements.set_point_id,
            ("TEST",)
        )
    ]
    table = Table(
        "Commands",
        Column("Available", justify="center")
    )
    with Live(table, console=console):
        for subsystem, cmd, params in tests:
            response = cmd(*params)
            if response.value is not None:
                result = ":white_check_mark:"
                logger.error(f"{subsystem} unavailable ({response})")
            else:
                result = ":x:"

            table.add_row(subsystem, result)

    logger.info("Tests complete")


def main(
    port: str,
    protocol: str,
    baud: int = 9600,
    timeout: int = 15,
    attempts: int = 1,
    sync_after_timeout: bool = False
) -> None:
    logger = getLogger("iman.protocoltest")
    try:
        with open_serial(
            port,
            speed=baud,
            timeout=timeout,
            attempts=attempts,
            sync_after_timeout=sync_after_timeout,
            logger=logger.getChild("com")
        ) as com:
            try:
                if protocol == "geocom":
                    tps = GeoCom(
                        com,
                        logger=logger.getChild("instrument")
                    )
                    tests_geocom(tps, logger)
                elif protocol == "gsidna":
                    dna = GsiOnlineDNA(
                        com,
                        logger=logger.getChild("instrument")
                    )
                    tests_gsidna(dna, logger)
            except Exception:
                print_error("An exception occured while running the tests")
                logger.exception(
                    "An exception occured while running the tests"
                )

    except (ConnectionRefusedError, ConnectionError) as e:
        print_error(f"Connection was not successful ({e})")
        logger.exception("Connection was not successful")
