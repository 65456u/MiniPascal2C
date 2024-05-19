import argparse

from mp2c import Converter


def main():
    """
    The main function of the program.

    This function creates an argument parser and reads the input and output file paths from the command line arguments.
    If an input file is provided, it reads the file, converts the code using the Converter class, and writes the result
    to the output file (if provided) or prints it to the console. If no input file is provided, it prints an error message.

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help = "input file")
    parser.add_argument("-o", "--output", help = "output file")
    args = parser.parse_args()

    if args.input:
        with open(args.input, "r") as file:
            input_code = file.read()
        converter = Converter()
        result = converter.convert(input_code)
        for error in result.error_messages:
            print(error)
        print(result.error_info)
        if args.output:
            with open(args.output, "w") as file:
                file.write(result.code)
        else:
            print(result.code)

    else:
        print("No input file provided")


if __name__ == '__main__':
    main()
