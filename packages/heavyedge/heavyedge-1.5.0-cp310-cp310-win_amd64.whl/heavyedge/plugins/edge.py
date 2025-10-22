"""Commands for edge data manipulation."""

import pathlib

from heavyedge.cli.command import Command, register_command

PLUGIN_ORDER = 1.0


@register_command("scale", "Scale edge profiles")
class ScaleCommand(Command):
    def add_parser(self, main_parser):
        scale = main_parser.add_parser(
            self.name,
            description="Scale edge profiles.",
            epilog="The resulting hdf5 file is in 'ProfileData' structure.",
        )
        scale.add_argument(
            "profiles",
            type=pathlib.Path,
            help="Path to preprocessed profile data in 'ProfileData' structure.",
        )
        scale.add_argument(
            "--type",
            choices=["area", "plateau"],
            default="area",
            help="Scaling type (default=area).",
        )
        scale.add_argument("-o", "--output", type=pathlib.Path, help="Output file path")

    def run(self, args):
        import numpy as np

        from heavyedge.io import ProfileData

        self.logger.info(f"Scaling profiles: {args.profiles}")

        with ProfileData(args.profiles) as data:
            _, M = data.shape()
            x = data.x()
            res = data.resolution()
            name = data.name()

            Ys, Ls, names = data[:]

        if args.type == "area":
            Ys[np.arange(M)[None, :] >= Ls[:, None]] = 0
            Ys /= np.trapezoid(Ys, x, axis=1)[:, np.newaxis]
            Ys[np.arange(M)[None, :] >= Ls[:, None]] = np.nan
        elif args.type == "plateau":
            Ys /= Ys[:, [0]]
        else:
            raise NotImplementedError

        with ProfileData(args.output, "w").create(M, res, name) as out:
            out.write_profiles(Ys, Ls, names)

        self.logger.info(f"Scaled profiles: {out.path}")


@register_command("trim", "Trim edge profiles")
class TrimCommand(Command):
    def add_parser(self, main_parser):
        trim = main_parser.add_parser(
            self.name,
            description="Trim edge profiles by a fixed width.",
            epilog=(
                "Width unit is determined by the resolution of 'profile'. "
                "The resulting hdf5 file is in 'ProfileData' structure."
            ),
        )
        trim.add_argument(
            "profiles",
            type=pathlib.Path,
            help="Path to preprocessed profile data in 'ProfileData' structure.",
        )
        trim.add_config_argument(
            "--width",
            type=float,
            help="Edge width. If not passed, length of the shortest profile.",
        )
        trim.add_argument("-o", "--output", type=pathlib.Path, help="Output file path")

    def run(self, args):
        import numpy as np

        from heavyedge.io import ProfileData

        self.logger.info(f"Trimming profiles: {args.profiles}")

        with ProfileData(args.profiles) as data:
            _, M = data.shape()
            res = data.resolution()
            name = data.name()

            Ys, Ls, names = data[:]

            if args.width is None:
                w = Ls.min()
            else:
                w = int(args.width * res)

        mask1 = np.repeat(np.arange(M)[None, :] <= w, len(Ys), axis=0)
        mask2 = (np.arange(M)[None, :] >= (Ls - w)[:, None]) & (
            np.arange(M)[None, :] <= Ls[:, None]
        )
        Ys[mask1] = Ys[mask2]
        Ys[:, w + 1 :] = np.nan

        with ProfileData(args.output, "w").create(M, res, name) as out:
            out.write_profiles(Ys, np.full(len(Ys), w), names)

        self.logger.info(f"Trimmed profiles: {out.path}")


@register_command("pad", "Pad edge profiles")
class PadCommand(Command):
    def add_parser(self, main_parser):
        pad = main_parser.add_parser(
            self.name,
            description="Pad edge profiles to a fixed width.",
            epilog=(
                "Width unit is determined by the resolution of 'profile'. "
                "The resulting hdf5 file is in 'ProfileData' structure."
            ),
        )
        pad.add_argument(
            "profiles",
            type=pathlib.Path,
            help="Path to preprocessed profile data in 'ProfileData' structure.",
        )
        pad.add_config_argument(
            "--width",
            type=float,
            help="Edge width. If not passed, length of the shortest profile.",
        )
        pad.add_argument("-o", "--output", type=pathlib.Path, help="Output file path")

    def run(self, args):
        import numpy as np

        from heavyedge.io import ProfileData

        self.logger.info(f"Padding profiles: {args.profiles}")

        with ProfileData(args.profiles) as data:
            _, M = data.shape()
            res = data.resolution()
            name = data.name()

            Ys, Ls, names = data[:]

            if args.width is None:
                w = Ls.max()
            else:
                w = int(args.width * res)

        new_Ys = np.full(Ys.shape, np.nan)
        new_Ys[:, :w] = Ys[:, :1]

        mask1 = ((w - Ls)[:, None] <= np.arange(M)[None, :]) & (
            np.arange(M)[None, :] <= w
        )
        mask2 = np.arange(M)[None, :] <= Ls[:, None]
        new_Ys[mask1] = Ys[mask2]

        with ProfileData(args.output, "w").create(M, res, name) as out:
            out.write_profiles(new_Ys, np.full(len(new_Ys), w), names)

        self.logger.info(f"Padded profiles: {out.path}")
