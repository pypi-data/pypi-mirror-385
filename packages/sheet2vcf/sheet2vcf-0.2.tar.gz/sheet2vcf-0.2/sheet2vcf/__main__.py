from .converter import convert_csv_to_vcf

def main():
    file = input("Enter CSV file name: ")
    convert_csv_to_vcf(file)

if __name__ == "__main__":
    main()

