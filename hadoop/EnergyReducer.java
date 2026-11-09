package org.apache.hadoop.energymonitoring;

import java.io.IOException;
import java.text.DecimalFormat;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;

/**
 * EnergyReducer
 * Receives grouped country keys and their respective consumption values.
 * Computes:
 * 1. Total energy consumption (kWh)
 * 2. Average energy consumption (kWh)
 * 3. Total reading count
 * Emits Key: Country, Value: "Total_kWh\tAvg_kWh\tCount"
 */
public class EnergyReducer extends Reducer<Text, DoubleWritable, Text, Text> {

    private final static DecimalFormat df = new DecimalFormat("#.##");
    private final Text result = new Text();

    @Override
    protected void reduce(Text key, Iterable<DoubleWritable> values, Context context)
            throws IOException, InterruptedException {

        double totalConsumption = 0.0;
        long count = 0;

        for (DoubleWritable val : values) {
            totalConsumption += val.get();
            count++;
        }

        double averageConsumption = (count > 0) ? (totalConsumption / count) : 0.0;

        // Output format: Total_kWh \t Avg_kWh \t Count
        String outStr = String.format("Total: %s kWh\tAvg: %s kWh\tReadings: %d",
                df.format(totalConsumption), df.format(averageConsumption), count);

        result.set(outStr);
        context.write(key, result);
    }
}

