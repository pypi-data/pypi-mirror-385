import csv

def convert_csv_to_vcf(input_file, output_file="numbers.vcf"):
    with open(input_file, newline='', encoding='utf-8') as csvfile, open(output_file, 'w', encoding='utf-8') as vcf:
        reader = csv.DictReader(csvfile)
        count = 1

        for row in reader:
            phone = row.get('phone', '').strip()
            if not phone:
                continue

            phone = phone.replace(" ", "").replace("-", "")
            name = f"Contact {count}"

            vcf.write("BEGIN:VCARD\n")
            vcf.write("VERSION:3.0\n")
            vcf.write(f"N:{name};;;;\n")
            vcf.write(f"FN:{name}\n")
            vcf.write(f"TEL;TYPE=CELL:{phone}\n")
            vcf.write("END:VCARD\n\n")

            count += 1

    print(f"✅ {output_file} created successfully with {count-1} contacts.")

