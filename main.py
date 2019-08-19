import argparse



def write_data(filename_target, data):
    if not data:
        return
    # for d in data:
    #     print(d)
    with open(filename_target, 'a') as f_target:
        columns = ['id', 'p_x', 'p_y', 'p_z', 'e', 'm', 'xProd', 'yProd', 'zProd', 'tProd', 'tau']
        title = '\t'.join(columns) + '\n'
        f_target.write(title)
        for row in data:
            f_target.write('\t'.join(row) + '\n')


def process_data(id_KL0, raw_data, mother, daughter, filename_target):
    # get the KL0 itself
    data = [raw_data[id_KL0]]

    # get daughters of KL0
    for i in daughter[id_KL0]:
        data.append(raw_data[i])

    # get the pion from the grandmother of KL0
    grandmother = mother[mother[id_KL0]]
    for j in daughter[grandmother]:
        if raw_data[j][0].endswith('211'):
            pion = j
            break
    data.append(raw_data[pion])

    write_data(filename_target, data)


def main():
    parser = argparse.ArgumentParser(description='Pythia Data')
    parser.add_argument(
        '-s',
        '--fn_source',
        type=str,
        nargs='?',
        default=1,
        help='name of source file'
    )
    parser.add_argument(
        '-t',
        '--fn_target',
        type=str,
        nargs='?',
        default=1,
        help='name of target file'
    )

    args = parser.parse_args()
    filename_source = args.fn_source
    filename_target = args.fn_target

    f_source = open(filename_source, 'r')
    line = f_source.readline()

    while line:
        if line.startswith(' --------  PYTHIA Event Listing  (complete event)'):
            # check bad event, such as the first one which is always bad
            for i in range(3):
                line = f_source.readline()
            row = line.split()
            if row[0] != 'scale':
                line = f_source.readline()
                continue

            KL0 = []  # store the id of all the K_L0 in each event
            raw_data = []
            mother = {}
            daughter = {}
            while line and not line.startswith(' --------  End PYTHIA Event Listing'):
                if row and row[0].isnumeric():
                    if row[2] == '(K_L0)':
                        KL0.append(int(row[0]))
                    raw_data.append([row[1]] + row[10:15])
                    mother[int(row[0])] = int(row[4])
                    daughter[int(row[0])] = list(range(int(row[6]), int(row[7]) + 1))
                elif row and row[0] == 'mothers:':
                    assert True  # implement later, double check whether mother and daughter are consistent
                elif len(row) == 7 and raw_data and len(raw_data[-1]) == 6:
                    raw_data[-1].extend(row[2:])

                line = f_source.readline()
                row = line.split()

            # write all K_L0 in the current event
            for id_KL0 in KL0:
                process_data(id_KL0, raw_data, mother, daughter, filename_target)

        line = f_source.readline()

    f_source.close()


if __name__ == '__main__':
    main()