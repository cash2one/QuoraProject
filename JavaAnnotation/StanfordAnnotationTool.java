import java.io.IOException;
import org.apache.thrift.TException;
import concrete.tools.AnnotationException;
import edu.jhu.hlt.concrete.Communication;
import edu.jhu.hlt.concrete.stanford.StanfordAgigaPipe;
import edu.jhu.hlt.concrete.util.ConcreteException;
import edu.jhu.hlt.concrete.util.CommunicationUtils;
import edu.jhu.hlt.concrete.serialization.CommunicationSerializer;
import edu.jhu.hlt.concrete.communications.SuperCommunication;

import java.util.List;
import java.util.ArrayList;
import java.io.*;
import java.util.Arrays;
import java.nio.file.InvalidPathException;
import java.nio.file.Path;

import org.apache.log4j.Logger;
import org.apache.log4j.Level;

public class StanfordAnnotationTool {

	private final StanfordAgigaPipe pipe;
	private final File in;
	private final File out;
	
	/**
	 * @throws IOException 
	 * 
	 */

	public StanfordAnnotationTool(File in, File out) throws IOException {
		this.pipe = new StanfordAgigaPipe();
		this.in = in;
		this.out = out;
	}

	public Communication annotate(Communication c) throws AnnotationException {
		try {
			return this.pipe.process(c);
		} catch (TException | IOException | ConcreteException e) {
			throw new AnnotationException(e);
		}
	}

	public void annotateDir(String dir) throws IOException, ConcreteException, AnnotationException {
		File newDir = new File(this.out + "/" + dir);
		File inDir = new File(this.in + "/" + dir);
		newDir.mkdirs();
		for(File thread : inDir.listFiles()) {
			// Needed because of .DS_Store files on OSX
			if(!thread.isDirectory()) {
				continue;
			}
			for(File commFile : thread.listFiles()) {
				if(commFile.getName().endsWith(".comm")) {
					System.out.println("============FILE============");
					System.out.println(commFile);
					System.out.println("============================\n\n");
					try{
						ArrayList<Path> paths = new ArrayList<Path>();
						paths.add(commFile.toPath());
						List<Communication> commList = CommunicationUtils.loadCommunicationsFromPaths(paths);
						if(commList.size() > 0) {
							Communication comm = commList.get(0);
							comm = annotate(comm);
							SuperCommunication superComm = new SuperCommunication(comm);

							String outDir = newDir.toString() + "/" + thread.getName() + "/";
							File f = new File(outDir);
							f.mkdirs();

							superComm.writeToFile(outDir + commFile.getName(), true);

						}
					} catch(InvalidPathException|AnnotationException e) {
						System.err.println("(!!!!) ERROR thrown on file " + commFile + "\n" + e);
					}
				}
			}
		}
	}

	public static void main(String[] args) throws IOException, ConcreteException, AnnotationException {
		String input_dir = "../data_new";
		String output_dir = "annotated_data";//"/export/a04/wpovell/annotated";
		if(args.length > 0) {
			input_dir = args[0];
		}
		if(args.length > 1) {
			output_dir = args[1];
		}

		File out = new File(output_dir);
		File in = new File(input_dir);


		// OLD, NEEDS TO BE SERIALIZED
		if(!out.isDirectory()) {
			out.mkdir();
		}
		System.out.println("Initializing Standford Annotation Tool\n=======================");
		StanfordAnnotationTool tool = new StanfordAnnotationTool(in, out);

		if(args.length > 2) {
			tool.annotateDir(args[2]);
		}

		System.out.println("\nWalking through data\n=======================");
		File newDir;
		for(File d1 : in.listFiles()) {
			String append1 = d1.getName();
			for(File d2 : d1.listFiles()) {
				String append2 = append1 + "/" + d2.getName();
				for(File d3 : d2.listFiles()) {
					String append3 = append2 + "/" + d3.getName();
					tool.annotateDir(append3);
				}
			}
		}
	}
}