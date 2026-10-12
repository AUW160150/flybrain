from .graph_rnn import GraphRNN
from .diagonal_lm import DiagonalLM
from .gru_lm import GRULM, choose_gru
from .transformer_lm import TransformerLM, choose_transformer

CONDITIONS=['FLY-TOPOLOGY','DEGREE-REWIRED','RANDOM-DENSITY','PARAMETER-MATCHED-GRU','NO-CROSS-NODE-RECURRENCE']

def accounting(model):
    total=sum(p.numel() for p in model.parameters())
    active=sum(p.numel() for p in model.parameters() if p.requires_grad)
    recurrent=sum(p.numel() for name,p in model.named_parameters() if name=='theta' or name.startswith('gru.'))
    active_core=sum(p.numel() for name,p in model.named_parameters() if p.requires_grad and (name=='theta' or name.startswith('gru.')))
    bias_count=model.bias.numel() if isinstance(model,GraphRNN) else 0
    graph_storage=sum(b.numel()*b.element_size() for b in model.buffers())
    return {'total_parameters':total,'active_trainable_parameters':active,'recurrent_parameters':recurrent,
            'recurrent_edge_parameters':model.theta.numel() if isinstance(model,GraphRNN) and not isinstance(model,DiagonalLM) else 0,
            'diagonal_parameters':model.theta.numel() if isinstance(model,DiagonalLM) else 0,
            'recurrent_bias_parameters':bias_count,
            'active_recurrent_parameters':active_core,'interface_parameters':total-recurrent-bias_count,
            'nontrainable_graph_storage_bytes':graph_storage}

def build(condition,graph,config,seed):
    n,d=len(graph.ids),config['d']
    target=512*d+2*n*d+n+256+len(graph.source)
    if condition=='PARAMETER-MATCHED-GRU':
        h,count=choose_gru(d,target); model=GRULM(d,h,seed)
        assert accounting(model)['active_trainable_parameters']==count
    elif condition=='TRANSFORMER':
        layers,ff,count=choose_transformer(d,config['context'],target)
        model=TransformerLM(d,ff,layers,config['context'],seed)
        assert accounting(model)['active_trainable_parameters']==count
    elif condition=='NO-CROSS-NODE-RECURRENCE': model=DiagonalLM(n,d,seed,config['execution'])
    else:
        initialization={'COUNT-INIT':'count','SHUFFLED-COUNT-INIT':'shuffled-count'}.get(condition,'uniform')
        model=GraphRNN(n,d,graph.source,graph.target,seed,execution=config['execution'],
                       counts=graph.counts,initialization=initialization)
        if condition=='FROZEN-FLY': model.theta.requires_grad_(False)
    return model
