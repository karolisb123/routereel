# RouteReel

A zero-dependency Python CLI that turns a plain CSV of delivery stops into an
efficient driving route. Point it at your stops, name your depot, and it returns
the order to visit them in, the mileage between each stop, and the total distance
for the run.

Built for the everyday dispatch problem: you have a truck, a depot, and a dozen
drops — what's the shortest sensible way to hit them all and get back?

## How it works

RouteReel solves a small [Traveling Salesman Problem](https://en.wikipedia.org/wiki/Travelling_salesman_problem):

1. **Distance** between stops is computed with the haversine formula, so mileage
   reflects real great-circle distance from latitude/longitude, not a flat grid.
2. **A first route** is built with a nearest-neighbor heuristic — from each stop,
   hop to the closest one you haven't visited yet.
3. **The route is polished** with a 2-opt pass that repeatedly un-crosses the path
   by reversing segments whenever doing so shortens the total.

The result is close to optimal for the stop counts a single driver handles in a
day, and it runs instantly with no external libraries.

## Install

```bash
git clone https://github.com/YOUR_USERNAME/routereel.git
cd routereel
python3 -m routereel.cli plan sample_data/stops.csv
```

Or install it as a command:

```bash
pip install -e .
routereel plan sample_data/stops.csv
```

## Usage

```bash
# Optimize starting from the first stop, returning to it at the end
python3 -m routereel.cli plan stops.csv

# Start from a named depot
python3 -m routereel.cli plan stops.csv -d "Bolingbrook Depot"

# One-way run that doesn't return to the depot
python3 -m routereel.cli plan stops.csv -d "Bolingbrook Depot" --one-way
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `-d`, `--depot` | Name of the starting depot | first stop in the file |
| `--one-way` | Don't return to the depot at the end | returns to depot |

## CSV format

Your stops file needs three columns:

```
stop,lat,lon
Bolingbrook Depot,41.6986,-88.0684
Naperville,41.7508,-88.1535
Aurora,41.7606,-88.3201
```

A ready-to-run example is in [`sample_data/stops.csv`](sample_data/stops.csv).

## Example output

```
Depot: Bolingbrook Depot
Stops: 10   Return to depot: yes

=== Optimized Route ===
   1. Bolingbrook Depot
   2. Woodridge  (+1.8 mi)
   3. Downers Grove  (+6.4 mi)
   ...
      ↩ return to Bolingbrook Depot  (+3.7 mi)

=== Summary ===
  Total distance     61.4 mi
  Naive nearest-nbr  64.9 mi
  Saved by 2-opt     3.5 mi (5.4%)
```

## Running tests

```bash
python3 -m unittest discover tests
```

## License

MIT — see [LICENSE](LICENSE).
