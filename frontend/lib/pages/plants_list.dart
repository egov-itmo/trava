import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:landscaping_frontend/config/config.dart';
import 'package:landscaping_frontend/entities/plants.dart';

class PlantsListPage extends StatefulWidget {
  const PlantsListPage({super.key});

  @override
  State<PlantsListPage> createState() => _PlantsListPageState();
}

class _PlantsListPageState extends State<PlantsListPage> {
  late Future<Plants> futurePlants;

  @override
  void initState() {
    super.initState();
    futurePlants = _fetch();
  }

  @override
  Widget build(BuildContext context) {
    var theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.all(8),
      child: FutureBuilder<Plants>(
          future: futurePlants,
          builder: (context, snapshot) {
            if (snapshot.hasData) {
              return PlantsTable(snapshot.data!.plants);
            } else if (snapshot.hasError) {
              return Text(
                '${snapshot.error}',
                style: TextStyle(color: theme.colorScheme.error),
              );
            }
            return const CircularProgressIndicator();
          }),
    );
  }

  Future<Plants> _fetch() async {
    final response =
        await http.get(Uri.parse('${appConfig.apiHost}/api/plants/all'));

    if (response.statusCode == 200) {
      return Plants.fromJson(jsonDecode(utf8.decode(response.bodyBytes)));
    } else {
      throw Exception('Ошибка загрузки (${response.statusCode})');
    }
  }
}

class PlantsTable extends StatelessWidget {
  final List<Plant> plants;

  const PlantsTable(this.plants, {super.key});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      scrollDirection: Axis.vertical,
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Table(
          border: TableBorder.all(),
          columnWidths: const {
            0: FixedColumnWidth(150),
            1: FixedColumnWidth(150),
            2: FixedColumnWidth(120),
            3: FixedColumnWidth(80),
            4: FixedColumnWidth(80),
            5: FixedColumnWidth(80),
            6: FixedColumnWidth(110),
            7: FixedColumnWidth(115),
            8: FixedColumnWidth(105),
            9: FixedColumnWidth(100),
          },
          children: [
            TableRow(
              children: [
                "Название",
                "Латинское название",
                "Род",
                "Тип",
                "Высота",
                "Размер кроны",
                "Агрессивность",
                "Выживаемость",
                "Инвазивность",
                "Фото",
              ]
                  .map(
                    (String text) => Padding(
                      padding: const EdgeInsets.all(2),
                      child: Center(
                        child: Text(
                          text,
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                      ),
                    ),
                  )
                  .toList(),
            ),
            for (Plant plant in plants) plant.toRow()
          ],
        ),
      ),
    );
  }
}
