// Descompila todas as funções e grava o C num arquivo só (para busca de padrões com grep).
// Uso (headless): -postScript DecompAll.java <saida.c>
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import java.io.*;

public class DecompAll extends GhidraScript {
    @Override
    public void run() throws Exception {
        PrintWriter out = new PrintWriter(new FileWriter(getScriptArgs()[0]));
        DecompInterface di = new DecompInterface();
        di.openProgram(currentProgram);
        for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
            if (monitor.isCancelled()) break;
            DecompileResults r = di.decompileFunction(f, 30, monitor);
            out.println("\n// ===== " + f.getName() + " @ " + f.getEntryPoint());
            if (r.decompileCompleted()) out.println(r.getDecompiledFunction().getC());
        }
        out.close();
    }
}
