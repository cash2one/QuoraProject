import org.apache.commons.io.FileUtils;
import org.apache.commons.compress.archivers.tar.TarArchiveInputStream;
import org.apache.commons.compress.archivers.tar.TarArchiveEntry;
import org.apache.commons.compress.archivers.tar.TarArchiveOutputStream;
import org.apache.commons.compress.compressors.gzip.GzipCompressorInputStream;
import org.apache.commons.compress.compressors.gzip.GzipCompressorOutputStream;

import org.apache.commons.cli.Options;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.BasicParser;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.ParseException;


import java.util.Collection;
import java.util.ArrayList;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.ByteArrayOutputStream;
import java.io.FileNotFoundException;
import java.io.BufferedOutputStream;
import java.io.FileOutputStream;

import edu.jhu.hlt.concrete.serialization.CompactCommunicationSerializer;
import edu.jhu.hlt.concrete.Communication;
import edu.jhu.hlt.concrete.util.ConcreteException;
import edu.jhu.hlt.concrete.stanford.StanfordAgigaPipe;
import concrete.tools.AnnotationException;

public class AnnotationTool {
	String INPUT_DIRECTORY, OUTPUT_DIRECTORY;
	File loadFile;
	StanfordAgigaPipe pipe;
	public AnnotationTool(String[] args) {
		Options options = new Options();
		options.addOption("i", true, "input directory");
		options.addOption("o", true, "output directory");
		options.addOption("f", true, "file to open");

		CommandLineParser parser = new BasicParser();
		CommandLine cmd = null;
		try {
			cmd = parser.parse( options, args);
		} catch(ParseException e) {
			e.printStackTrace();
			System.exit(1);
		}

		INPUT_DIRECTORY = cmd.getOptionValue("i");
		if(INPUT_DIRECTORY == null)
			INPUT_DIRECTORY = "../data_new"; // /export/a04/wpovell/concrete_files

		OUTPUT_DIRECTORY = cmd.getOptionValue("d");
		if(OUTPUT_DIRECTORY == null)
			OUTPUT_DIRECTORY = "../data_annotated"; // /export/a04/wpovell/concrete_annotated

		loadFile = null;
		String loadFileS = cmd.getOptionValue("f");
		if(loadFileS != null) {
			loadFileS = INPUT_DIRECTORY + "/" + loadFileS;
			if(!loadFileS.endsWith(".tar.gz")) {
				loadFileS += ".tar.gz";
			}
			loadFile = new File(loadFileS);
		}

		System.out.println("Initializing Standford Annotation Tool\n=======================");
		try {
			pipe = new StanfordAgigaPipe();
		} catch(IOException e) {
			e.printStackTrace();
		}
	}

	public void proccessTarFile(File f) {
			System.out.println(f);
			// Used to turn communication files into bytes
			CompactCommunicationSerializer ser = new CompactCommunicationSerializer();

			File outFile = new File(f.getParent().replace(INPUT_DIRECTORY, OUTPUT_DIRECTORY));
			outFile.mkdirs(); // Make all parent dirs for output file
			outFile = new File(outFile + "/" + f.getName());
			try {
				TarArchiveOutputStream tarOut = new TarArchiveOutputStream(new GzipCompressorOutputStream(new BufferedOutputStream(new FileOutputStream(outFile))));
				final TarArchiveInputStream tarIn = new TarArchiveInputStream(new GzipCompressorInputStream( new FileInputStream(f)));
				TarArchiveEntry entry;
				while ( ( entry = tarIn.getNextTarEntry() ) != null ) {
					String name = entry.getName();

					// Read entry
					byte[] btoRead = new byte[1024];
					ByteArrayOutputStream bout = new ByteArrayOutputStream();
					int len = 0;
					while ((len = tarIn.read(btoRead)) != -1) {
						bout.write(btoRead, 0, len);
					}
					bout.close();

					// Create new TarEntry
					TarArchiveEntry outEntry = new TarArchiveEntry(name);
					byte[] dataBytes = null;

					if(name.endsWith("comm")) {
						try {
							Communication c = ser.fromBytes(bout.toByteArray());
							System.out.println(name);
							c = pipe.process(c); // Annotate Communication File
							dataBytes = ser.toBytes(c);
						} catch(IOException|AnnotationException|ConcreteException e) {
							e.printStackTrace();
						}
					} else {
						dataBytes = bout.toByteArray();
					}

					// Add entry to tar
					outEntry.setSize(dataBytes.length);
					tarOut.putArchiveEntry(outEntry);
					tarOut.write(dataBytes);
					tarOut.closeArchiveEntry();
				}
				tarIn.close();
				tarOut.close();
			} catch (IOException e) {
				e.printStackTrace();
			}
	}

	public static void main(String[] args) {
		AnnotationTool tool = new AnnotationTool(args);

		if(tool.loadFile != null) {
			tool.proccessTarFile(tool.loadFile);
		} else {
			// Find all .tar.gz files in input directory
			String[] exts = {"gz"};
			Collection<File> files = FileUtils.listFiles(new File(tool.INPUT_DIRECTORY), exts, true);

			System.out.println("Looping Through Files\n=======================");
			for(File f : files) {
				tool.proccessTarFile(f);
			}
		}
	}
}