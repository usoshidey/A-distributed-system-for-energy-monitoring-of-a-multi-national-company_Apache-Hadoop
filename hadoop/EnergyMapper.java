package org.apache.hadoop.energymonitoring;

import java.io.IOException;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

/**
 * EnergyMapper
 * Reads raw energy telemetry records in CSV format from HDFS.
 * Extracts Country as Key and Energy Consumption (kWh) as Value.
 * Input CSV Format:
 * reading_id,meter_id,company_id,branch_name,country,timestamp,energy_kwh,voltage,current,power_factor
 */
public class EnergyMapper extends Mapper<LongWritable, Text, Text, DoubleWritable> {

    private final static Text countryKey = new Text();
    private final static DoubleWritable consumptionVal = new DoubleWritable();

    @Override
    protected void map(LongWritable key, Text value, Context context)
            throws IOException, InterruptedException {

        String line = value.toString().trim();
        if (line.isEmpty()) {
            return;
        }

        // Skip header row if present
        if (line.startsWith("reading_id") || line.contains("energy_kwh")) {
            return;
        }

        // Split CSV by comma
        String[] tokens = line.split(",");
        // Ensure valid token count (expected 10 columns)
        if (tokens.length >= 7) {
            try {
                // tokens[4] = Country, tokens[6] = energy_kwh
                String country = tokens[4].trim();
                double consumption = Double.parseDouble(tokens[6].trim());

                if (!country.isEmpty() && consumption >= 0.0) {
                    countryKey.set(country);
                    consumptionVal.set(consumption);
                    context.write(countryKey, consumptionVal);
                }
            } catch (NumberFormatException e) {
                // Skip malformed records and increment Hadoop counter
                context.getCounter("EnergyMonitoring", "MalformedRecords").increment(1);
            }
        } else {
            context.getCounter("EnergyMonitoring", "CorruptedRows").increment(1);
        }
    }
}

