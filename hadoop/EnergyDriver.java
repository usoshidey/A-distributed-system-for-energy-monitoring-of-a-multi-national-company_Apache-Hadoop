package org.apache.hadoop.energymonitoring;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.conf.Configured;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.util.Tool;
import org.apache.hadoop.util.ToolRunner;

/**
 * EnergyDriver
 * Main configuration and execution driver for the Distributed Energy Monitoring MapReduce Job.
 * Usage:
 *   hadoop jar energy-monitoring-mr.jar org.apache.hadoop.energymonitoring.EnergyDriver <input_path> <output_path>
 */
public class EnergyDriver extends Configured implements Tool {

    @Override
    public int run(String[] args) throws Exception {
        if (args.length < 2) {
            System.err.println("Usage: EnergyDriver <input_path> <output_path>");
            System.err.println("Example: EnergyDriver /energy-monitoring/raw-data/energy_data.csv /energy-monitoring/processed-data/country_summary");
            return -1;
        }

        Configuration conf = getConf();
        Job job = Job.getInstance(conf, "Multinational Corporate Energy Monitoring - Aggregation");

        job.setJarByClass(EnergyDriver.class);

        // Set Mapper and Reducer
        job.setMapperClass(EnergyMapper.class);
        job.setCombinerClass(EnergyCombiner.class); // Optional combiner for local aggregation optimization
        job.setReducerClass(EnergyReducer.class);

        // Mapper output key-value
        job.setMapOutputKeyClass(Text.class);
        job.setMapOutputValueClass(DoubleWritable.class);

        // Final output key-value
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(Text.class);

        Path inputPath = new Path(args[0]);
        Path outputPath = new Path(args[1]);

        FileInputFormat.addInputPath(job, inputPath);
        FileOutputFormat.setOutputPath(job, outputPath);

        // Clean output directory if already exists on HDFS
        FileSystem fs = FileSystem.get(conf);
        if (fs.exists(outputPath)) {
            System.out.println("Output directory " + outputPath + " already exists. Deleting previous output...");
            fs.delete(outputPath, true);
        }

        System.out.println("Submitting MapReduce Job to YARN Cluster...");
        boolean success = job.waitForCompletion(true);
        System.out.println("MapReduce Job finished with status: " + (success ? "SUCCESS" : "FAILED"));

        return success ? 0 : 1;
    }

    /**
     * Inner Combiner class for Map-side local pre-aggregation
     */
    public static class EnergyCombiner extends org.apache.hadoop.mapreduce.Reducer<Text, DoubleWritable, Text, DoubleWritable> {
        private final DoubleWritable result = new DoubleWritable();

        @Override
        protected void reduce(Text key, Iterable<DoubleWritable> values, Context context)
                throws IOException, InterruptedException {
            double sum = 0.0;
            for (DoubleWritable val : values) {
                sum += val.get();
            }
            result.set(sum);
            context.write(key, result);
        }
    }

    public static void main(String[] args) throws Exception {
        int exitCode = ToolRunner.run(new Configuration(), new EnergyDriver(), args);
        System.exit(exitCode);
    }
}

