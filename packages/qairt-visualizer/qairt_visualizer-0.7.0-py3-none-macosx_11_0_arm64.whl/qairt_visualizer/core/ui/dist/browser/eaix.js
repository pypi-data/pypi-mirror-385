// QAIRT Netron: Add model factory for the EAIX format
const eaix = {};

eaix.ModelFactory = class {

    async match(context) {
        const obj = await context.peek('json');
        return context.set('eaix', obj);
    }

    /*
     * EAIX is a JSON that adheres to Netron's Model object format, however it is based on an older version of Netron.
     * This method resolves the incompatibilities between the Model formats of the Netron version that EAIX is based on
     * and the version used in Visualizer
     */
    async open(context) {
        context.value.modules = context.value.graphs;
        delete context.value.graphs;
        return context.value;
    }
};

export const ModelFactory = eaix.ModelFactory;
// QAIRT Netron END
