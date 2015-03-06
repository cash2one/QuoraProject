import org.apache.commons.io.FileUtils;
import org.apache.commons.compress.archivers.tar.TarArchiveInputStream;
import org.apache.commons.compress.archivers.tar.TarArchiveEntry;
import org.apache.commons.compress.archivers.tar.TarArchiveOutputStream;
import org.apache.commons.compress.compressors.gzip.GzipCompressorInputStream;
import org.apache.commons.compress.compressors.gzip.GzipCompressorOutputStream;

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
	static String INPUT_DIRECTORY = "../data_new"; // /export/a04/wpovell/concrete_files
	static String OUTPUT_DIRECTORY = "../data_annotated"; // /export/a04/wpovell/concrete_annotated
	static StanfordAgigaPipe pipe;
	public static void main(String[] args) {
		System.out.println("Initializing Standford Annotation Tool\n=======================");
		try {
			pipe = new StanfordAgigaPipe();
		} catch(IOException e) {
			e.printStackTrace();
		}

		if(args.length > 0) {
			INPUT_DIRECTORY = args[0];
			if(args.length > 1) {
				OUTPUT_DIRECTORY = args[1];
			}
		}

		// Find all .tar.gz files in input directory
		String[] exts = {"gz"};
		Collection<File> files = FileUtils.listFiles(new File(INPUT_DIRECTORY), exts, true);

		// Used to turn communication files into bytes
		CompactCommunicationSerializer ser = new CompactCommunicationSerializer();

		System.out.println("Looping Through Files\n=======================");
		for(File f : files) {
			System.out.println(f);
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
	}
}