from Evaluation import GeoJsonReader
import csv


if __name__ == '__main__':
    csv_output = open('narges_original_text.csv', 'wt');
    csv_writer = csv.writer(csv_output)

    count = 0
    for i in range(1, 11):
        result_file_name = './narges result/1920-' + str(i) + '.png_EdditedByPixels.txt'
        result_obj = GeoJsonReader.load_json_file(result_file_name)


        for feature in result_obj['features']:
            text = feature['NameBeforeDictionary']
            text.replace(',', '')
            text.replace('\n', ' ')
            csv_writer.writerow([text])
            count += 1
