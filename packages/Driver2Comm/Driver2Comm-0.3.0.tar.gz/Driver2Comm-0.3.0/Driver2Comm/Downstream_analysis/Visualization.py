import pandas as pd
import numpy as np
import codecs
import os
from .CytoTalk_network  import c2c_network
from .CytoTalk_network import VACANT_EDGE_ID
from .CytoTalk_network import VACANT_VERTEX_LABEL
from .CytoTalk_network import VACANT_EDGE_COST
from queue import PriorityQueue
import collections


class Visualization(object):
    def __init__(self, association_test_ret, frequent_subgraphs):
        """

        :param association_test_ret: list of association test result, each element contaion:
        - internal: driver / tumor subtype of interested
        - idx of passed FP: index of significant frequent pattern/subgraph
        - internal vec : one hot encode vector of patient driver
        - pvalue of passed FP : pvalue of significant frequent pattern/subgraph
        :param frequent_subgraphs:
        """
        self.association_test_ret = association_test_ret #
        self.frequent_subgraphs = frequent_subgraphs
        #self.patient_driver = patient_driver
        self.pcsf_network = None
        self.original_network = None


    def read_graph_from_cytotalk_output(self, patientpath):
        """
        read communication networks from cytotalk outputs with edge cost
        :param self:
        :param patientpath: PATH that store cytotalk's output .
        This directory should contain subdirectory named celltypeA-cellTypeB
        :return:
        """
        original_network = c2c_network()
        pcsf_network = c2c_network()
        # read the final network
        celltype_list = os.listdir(patientpath)
        for celltype in celltype_list:
            pcsf_matrix = pd.read_table(os.path.join(patientpath, celltype, 'FinalNetwork.txt'))
            for i in range(pcsf_matrix.shape[0]):
                node1 = pcsf_matrix.loc[i, 'node1'].upper() + '__' + pcsf_matrix.loc[i, 'node1_type']
                node2 = pcsf_matrix.loc[i, 'node2'].upper() + '__' + pcsf_matrix.loc[i, 'node2_type']
                if not pcsf_network.vertices.__contains__(node1):
                    pcsf_network.add_vertex(node1)
                if not pcsf_network.vertices.__contains__(node2):
                    pcsf_network.add_vertex(node2)
                pcsf_network.add_edge(VACANT_EDGE_ID, node1, node2, int(pcsf_matrix.loc[i, 'is_ct_edge']),
                                      pcsf_matrix.loc[i, 'cost'])
        for celltype in celltype_list:
            original_matrix = pd.read_table(os.path.join(patientpath, celltype, 'IntegratedEdges.txt'))
            for i in range(original_matrix.shape[0]):
                node1 = original_matrix.loc[i, 'node1']
                node2 = original_matrix.loc[i, 'node2']
                gene1, celltype1 = node1.split('__')
                gene2, celltype2 = node2.split('__')
                # update annotation
                node1 = gene1.upper() + '__' + celltype1
                node2 = gene2.upper() + '__' + celltype2
                if not original_network.vertices.__contains__(node1):
                    original_network.add_vertex(node1)
                if not original_network.vertices.__contains__(node2):
                    original_network.add_vertex(node2)
                original_network.add_edge(VACANT_EDGE_ID, node1, node2, int(self.inequal_celltype(node1, node2)),
                                          original_matrix.loc[i, 'cost'])
        # construct an edge priority
        pcsf_network.sort_edges()
        original_network.sort_edges()
        self.pcsf_network = pcsf_network
        self.original_network = original_network
        return self
    def __read_graph_from_cytotalk_output(self, patientpath):
        """
        read communication networks from cytotalk outputs with edge cost
        :param self:
        :param patientpath: PATH that store cytotalk 's output .
        This directory should contain subdirectory named celltypeA-cellTypeB
        :return:
        """
        original_network = c2c_network()
        pcsf_network = c2c_network()
        # read the final network
        celltype_list = os.listdir(patientpath)
        for celltype in celltype_list:
            pcsf_matrix = pd.read_table(os.path.join(patientpath, celltype, 'FinalNetwork.txt'))
            for i in range(pcsf_matrix.shape[0]):
                node1 = pcsf_matrix.loc[i, 'node1'].upper() + '__' + pcsf_matrix.loc[i, 'node1_type']
                node2 = pcsf_matrix.loc[i, 'node2'].upper() + '__' + pcsf_matrix.loc[i, 'node2_type']
                if not pcsf_network.vertices.__contains__(node1):
                    pcsf_network.add_vertex(node1)
                if not pcsf_network.vertices.__contains__(node2):
                    pcsf_network.add_vertex(node2)
                pcsf_network.add_edge(VACANT_EDGE_ID, node1, node2, int(pcsf_matrix.loc[i, 'is_ct_edge']),
                                      pcsf_matrix.loc[i, 'cost'])
        for celltype in celltype_list:
            original_matrix = pd.read_table(os.path.join(patientpath, celltype, 'IntegratedEdges.txt'))
            for i in range(original_matrix.shape[0]):
                node1 = original_matrix.loc[i, 'node1']
                node2 = original_matrix.loc[i, 'node2']
                gene1, celltype1 = node1.split('__')
                gene2, celltype2 = node2.split('__')
                # update annotation
                node1 = gene1.upper() + '__' + celltype1
                node2 = gene2.upper() + '__' + celltype2
                if not original_network.vertices.__contains__(node1):
                    original_network.add_vertex(node1)
                if not original_network.vertices.__contains__(node2):
                    original_network.add_vertex(node2)
                original_network.add_edge(VACANT_EDGE_ID, node1, node2, int(self.inequal_celltype(node1, node2)),
                                          original_matrix.loc[i, 'cost'])
        # construct an edge priority
        pcsf_network.sort_edges()
        original_network.sort_edges()
        return pcsf_network,original_network
    def inequal_celltype(self, node1, node2, celltypelist=['Cd8+Tcells', 'Macrophages', 'Tumor']):
        for i in range(len(celltypelist)):
            if celltypelist[i] in node1:
                if celltypelist[i] in node2:
                    return False
        return True

    def get_ie_pathway(self, internal_gene, external_gene):
        pcsf_network = self.pcsf_network
        original_network = self.original_network
        return self.__get_ie_pathway(internal_gene, external_gene, pcsf_network, original_network)

    def __get_ie_pathway(self, internal_gene, external_gene, pcsf_network, original_network):
        """
        identify shortest pathway between internal_gene and external_gene in extend_network
        :param internal_gene:
        :param external_gene:
        :param pcsf_network:
        :param original_network:
        :return:
        """
        if internal_gene not in original_network.set_of_vlb or external_gene not in pcsf_network.set_of_vlb:
            return pd.DataFrame()
        internal_network = c2c_network()
        internal_network.add_vertex(internal_gene)
        if (internal_gene in pcsf_network.set_of_vlb):
            internal_network = self.__combine_network(internal_network, pcsf_network)
        else:
            original_network.sort_edges()
            internal_network = self.__extend_network(pcsf_network.set_of_vlb, internal_network, original_network)
            internal_network = self.__combine_network(internal_network, pcsf_network)
        external_network = c2c_network()
        if (external_gene in pcsf_network.set_of_vlb):
            external_network = self.__combine_network(internal_network, external_network)
        else:
            external_network.add_vertex(external_gene)
            original_network.sort_edges()
            external_network = self.__extend_network(pcsf_network.set_of_vlb, external_network, original_network)
        combined_network = self.__combine_network(internal_network, external_network)
        ret = self.__identify_ie_pathway_util(internal_gene, external_gene, combined_network)
        return ret

    def __extend_network(self, geneset, internal_network, original_network):
        while len(geneset & internal_network.set_of_vlb) < 1:
            internal_geneset = internal_network.set_of_vlb.copy()
            for node1 in internal_geneset:
                while not original_network.vertices[node1].edges_queue.empty():
                    cost, (_, node2) = original_network.vertices[
                        node1].edges_queue.get()  # get a shortest edge connected to node1
                    if node2 not in internal_geneset:
                        internal_network.add_vertex(node2)
                        internal_network.add_edge(VACANT_EDGE_ID, node1, node2,
                                                  original_network.vertices[node1].edges[node2].edge_type,
                                                  original_network.vertices[node1].edges[node2].edge_cost)
        # once jump out of circle, we find the intersect part between internal and external
        return internal_network

    def __combine_network(self, internal_network: c2c_network, external_network):
        # combined the internal network and external network to internal network
        combined_network = internal_network
        for label, vertex in external_network.vertices.items():
            if not combined_network.vertices.__contains__(label):
                combined_network.add_vertex(label)
            for label2, edge in vertex.edges.items():
                if not combined_network.vertices.__contains__(label2):
                    combined_network.add_vertex(label2)
                combined_network.add_edge(VACANT_EDGE_ID, label, label2, edge.edge_type, edge.edge_cost)
        return combined_network

    def __identify_ie_pathway_util(self, internal_gene, exteranl_gene, combination_network):
        '''
        utils:identify the shorest path from internal gene to external gene
        :param internal_gene:
        :param exteranl_gene:
        :param combination_network:
        :return:
        '''
        set_of_searched_vertices = set()
        set_of_unsearched_vertices = set()
        combination_network.sort_edges()
        set_of_searched_vertices.add(internal_gene)
        distance = {internal_gene: 0}
        prior_vertex = {internal_gene: VACANT_VERTEX_LABEL}
        closest_vertex_queue = PriorityQueue()
        for vlb, vertex in combination_network.vertices.items():
            if vlb != internal_gene:
                set_of_unsearched_vertices.add(vlb)
                distance[vlb] = float('inf')
                prior_vertex[vlb] = None
        while not combination_network.vertices[internal_gene].edges_queue.empty():
            cost, (node1, node2) = combination_network.vertices[internal_gene].edges_queue.get()
            distance[node2] = cost
            prior_vertex[node2] = node1
            closest_vertex_queue.put((cost, (node1, node2)))
        # start searching shortest path from internal to external
        while (not closest_vertex_queue.empty()) and (exteranl_gene in set_of_unsearched_vertices):
            _, (_, node2) = closest_vertex_queue.get()
            if node2 not in set_of_searched_vertices:
                set_of_searched_vertices.add(node2)
                set_of_unsearched_vertices.remove(node2)
                # update distance dict and prior dict
                while not combination_network.vertices[node2].edges_queue.empty():
                    cost, (_, node3) = combination_network.vertices[node2].edges_queue.get()
                    if node3 not in set_of_searched_vertices:
                        if cost + distance[node2] < distance[node3]:
                            distance[node3] = cost + distance[node2]
                            prior_vertex[node3] = node2
                        closest_vertex_queue.put((distance[node3], (node2, node3)))
        shortest_path_matrix = self.__get_shortest_path(internal_gene, exteranl_gene, prior_vertex,
                                                      combination_network)
        return shortest_path_matrix

    def __get_shortest_path(self, internal_gene, exteranl_node, prior_vertex: dict, combination_network):
        shortest_path = collections.defaultdict(list)
        node1 = prior_vertex[exteranl_node]
        node2 = exteranl_node
        while node2 != internal_gene:
            gene1,ct1 = node1.split('__')
            gene2, ct2 = node2.split('__')
            shortest_path['node1'].append(gene1)
            shortest_path['node2'].append(gene2)
            shortest_path['node1_type'].append(ct1)
            shortest_path['node2_type'].append(ct2)
            shortest_path['is_ct_edge'].append(bool(combination_network.vertices[node1].edges[node2].edge_type))
            shortest_path['cost'].append(combination_network.vertices[node1].edges[node2].edge_cost)
            if (node2 == exteranl_node):
                shortest_path['edge_role'].append('end')
            elif (node1 == internal_gene):
                shortest_path['edge_role'].append('start')
            else:
                shortest_path['edge_role'].append('intermediate')
            node2 = node1
            node1 = prior_vertex[node2]
        shortest_path_matrix = pd.DataFrame(shortest_path)
        shortest_path_matrix = shortest_path_matrix.reindex(index=shortest_path_matrix.index[::-1])
        return shortest_path_matrix

    def generate_top_k_ie_pathway(self, internal_node, k, patient_path):
        """

        :param internal_gene:
        :param k:
        :param patient_path:
        :param association_test_ret:
        :return:
        """
        print(patient_path)
        driver,ct = internal_node.split('__')
        for i in range(len(self.association_test_ret)):
            if self.association_test_ret[i]['internal'] == driver:
                association_test_ret = self.association_test_ret[i]
                break

        tested_FP_list = association_test_ret['idx of passed FP']
        shortest_path_network = pd.DataFrame()
        pcsf_network = self.pcsf_network
        original_network = self.original_network
        for i in range(k):
            if i == 9:
                print(1)
            g = self.frequent_subgraphs[tested_FP_list[i]].to_graph(
                gid=tested_FP_list[i])
            for vid, vertex in g.vertices.items():
                shortest_path_matrix = self.__get_ie_pathway(internal_node, vertex.vlb, pcsf_network,
                                                              original_network)
                if shortest_path_matrix.shape[0] > 0:
                    print(f'identifying pathway to {vertex.vlb} in {driver}-associated CCC signature {i + 1} ')
                shortest_path_network = pd.concat((shortest_path_network, shortest_path_matrix), axis=0)
        frequent_subgraph_matrix = self.__get_frequent_subgraph_matrix(k,association_test_ret)
        shortest_path_network = pd.concat((frequent_subgraph_matrix,shortest_path_network),axis=0)
        shortest_path_network = shortest_path_network.reset_index(drop=True)
        return shortest_path_network

    def generate_pathway_of_a_FP(self, internal_gene, frequent_graph, pcsf_network, original_network):
        """
        :param internal_gene:
        :param frequent_graph:
        :param pcsf_network:
        :param original_network:
        :return:
        """
        shortest_path_network = pd.DataFrame()
        for vid, vertex in frequent_graph.vertices.items():
            shortest_path_matrix = self.__get_ie_pathway(internal_gene, vertex.vlb, pcsf_network, original_network)
            shortest_path_network = pd.concat((shortest_path_network, shortest_path_matrix), axis=0)
        shortest_path_network = shortest_path_network.reset_index(drop=True)
        return shortest_path_network

    def generate_top_k_pathway_separated(self, internal_gene,tumor_cell_annotation, k, patients_path, outputdir='./result'):
        """
        generate top k IE pathway separately for all patient with this driver
        :param :internal_gene query driver gene
        :param k:
        :param patients_path:
        :param outputdir:
        :return:
        """
        patient_list = []
        internal_node = internal_gene + '__' + tumor_cell_annotation
        internal_idx = 0
        for name, driver in self.patient_driver.items():
            if (driver == internal_gene):
                patient_list.append(name)
        for i in range(len(self.association_test_ret)):
            if self.association_test_ret[i]['internal'] == internal_gene:
                internal_idx = i  # get the association test result corresponding to genome factor
                break
        association_test_ret = self.association_test_ret[internal_idx]
        tested_FP_list = association_test_ret['idx of passed FP']
        external_matrix = association_test_ret['external matrix']
        for patient in patient_list:
            print(patient)
            output_dir = os.path.join(outputdir, internal_gene, patient)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            patient_path = os.path.join(patients_path, patient)
            pcsf_network, original_network = self.__read_graph_from_cytotalk_output(patient_path)
            for i in range(k):
                if(external_matrix.loc[patient,tested_FP_list[i]]==0):
                    continue
                g = self.frequent_subgraphs[tested_FP_list[i]].to_graph(
                    gid=tested_FP_list[i])
                patient_shortest_network = self.generate_pathway_of_a_FP(internal_node, g, pcsf_network,
                                                                         original_network)
                if (patient_shortest_network.shape[0] > 0):
                    print('{} th frequent pattern'.format(tested_FP_list[i]))
                self.output_shortest_network_info_pre_FP(tested_FP_list[i], patient_shortest_network,
                                                         output_dir)
        return

    def generate_top_k_pathway_of_sample_with_same_genome_factor(self, internal_gene,tumor_cell_annotation, k, patients_path,
                                                                 outputdir='./result'):
        '''
        generate top k pathway of sample with same genome factor in order to see if they have a strong overlap
        :param genome_factor:
        :param k:
        :param outputdir:
        :return:
        '''
        patient_list = []
        internal_node = internal_gene[0] + '__'+ tumor_cell_annotation
        for name, driver in self.patient_driver.items():
            if (driver == internal_gene):
                patient_list.append(name)


        for patient in patient_list:
            output_dir = os.path.join(outputdir, internal_gene, patient)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            patient_path = os.path.join(patients_path, patient)
            patient_shortest_network = self.generate_top_k_ie_pathway(internal_node, k, patient_path)
            self.output_shortest_network_info(patient_shortest_network, output_dir)
            # self.output_network_sif(patient_shortest_network,output_dir+'/shortest_paths.sif')
            # patient_shortest_network.to_csv(output_dir+'/shortest_paths.txt',sep='\t',index = False)
        return

    def __get_frequent_subgraph_matrix(self, k,association_test_ret):
        """
        generate edge for frequent subgraph as a dataframe format and then concat to the shortest path
        :param k:
        :param association_test_ret:  assoicated result of interested Driver
        :return:
        """
        set_of_edge = set()
        fp_info = collections.defaultdict(list)
        for i in range(k):
            fpid = association_test_ret['idx of passed FP'][i]
            g = self.frequent_subgraphs[fpid].to_graph(gid = fpid)
            for vid,vertex in g.vertices.items():
                for toid in vertex.edges.keys():
                    node1 = vertex.vlb
                    node2 = g.vertices[toid].vlb
                    if (node1,node2) not in set_of_edge:
                        set_of_edge.add((node1,node2))
                        set_of_edge.add((node2,node1))
                        gene1, ct1 = node1.split('__')
                        gene2, ct2 = node2.split('__')
                        fp_info['node1'].append(gene1)
                        fp_info['node2'].append(gene2)
                        fp_info['node1_type'].append(ct1)
                        fp_info['node2_type'].append(ct2)
                        fp_info['is_ct_edge'].append(self.inequal_celltype(node1,node2))
                        fp_info['cost'].append(VACANT_EDGE_COST)
                        fp_info['edge_role'].append('frequent pathway')
        return  pd.DataFrame(fp_info)


    def generate_heatmap_of_pathway_overlap(self, inputdir, outputdir='./result'):
        patient_list = os.listdir(inputdir)
        num_patient = len(patient_list)
        overlap_heatmap = np.ones((num_patient, num_patient))
        for i in range(num_patient):
            for j in range(i + 1, num_patient):
                patient_i = pd.read_table(os.path.join(inputdir, patient_list[i], 'geneRole.txt'), sep='\t')
                patient_j = pd.read_table(os.path.join(inputdir, patient_list[j], 'geneRole.txt'), sep='\t')
                geneset_i = set(patient_i.loc[:, 'geneLabel'])
                geneset_j = set(patient_j.loc[:, 'geneLabel'])
                overlap_heatmap[i, j] = overlap_heatmap[j, i] = len(geneset_i & geneset_j) * 1.0 / min(
                    len(geneset_i), len(geneset_j))
        overlap_heatmap = pd.DataFrame(overlap_heatmap, index=patient_list, columns=patient_list)
        overlap_heatmap.to_csv(os.path.join(outputdir, 'overlap_heatmap.csv'))
        return overlap_heatmap

    def output_shortest_network_info_pre_FP(self, FP_id, network_matrix, output_dir='./result'):
        if (network_matrix.shape[0] == 0):
            return
        output_dir = os.path.join(output_dir, 'Frequent_pattern_' + str(FP_id))
        if (not os.path.exists(output_dir)):
            os.makedirs(output_dir)
        sif_path = os.path.join(output_dir, 'shortest_path.sif')
        generole_path = os.path.join(output_dir, 'geneRole.txt')
        matrix_path = os.path.join(output_dir, 'shortest_paths.txt')
        output_sif = codecs.open(sif_path, 'w', 'utf-8')
        output_geneRole = collections.defaultdict(list)
        set_of_vlb = set()
        set_of_elb = set()
        for i in range(network_matrix.shape[0]):
            node1 = network_matrix.loc[i, 'node1']
            node2 = network_matrix.loc[i, 'node2']
            if (network_matrix.loc[i, 'is_ct_edge']):
                interact = 'cross-talk'
            else:
                interact = 'intra-talk'
            edge_role = network_matrix.loc[i, 'edge_role']
            if (node1 not in set_of_vlb):
                output_geneRole['geneLabel'].append(node1)
                output_geneRole['geneRealName'].append(node1.split('__')[0].upper())
                output_geneRole['cellType'].append(node1.split('__')[1])

                if (edge_role == 'start'):
                    output_geneRole['Role'].append('internal_gene')
                else:
                    output_geneRole['Role'].append('intermediate_gene')
                set_of_vlb.add(node1)
            if (node2 not in set_of_vlb):
                output_geneRole['geneLabel'].append(node2)
                output_geneRole['geneRealName'].append(node2.split('__')[0].upper())
                output_geneRole['cellType'].append(node2.split('__')[1])
                if (edge_role == 'end'):
                    output_geneRole['Role'].append('external_gene')
                else:
                    output_geneRole['Role'].append('intermediate_gene')
                set_of_vlb.add(node2)
            if ((node1, node2) not in set_of_elb):
                set_of_elb.add((node1, node2))
                set_of_elb.add((node2, node1))
                output_sif.write('{}\t{}\t{}\n'.format(node1, interact, node2))
        output_sif.close()
        generole_matrix = pd.DataFrame(output_geneRole)
        generole_matrix.to_csv(generole_path, sep='\t', index=False)
        network_matrix.to_csv(matrix_path, sep='\t', index=False)
        return

    def output_shortest_network_info(self, network_matrix, output_dir='./result'):
        if (not os.path.exists(output_dir)):
            os.makedirs(output_dir)
        sif_path = os.path.join(output_dir, 'shortest_path.sif')
        generole_path = os.path.join(output_dir, 'geneRole.txt')
        matrix_path = os.path.join(output_dir, 'shortest_paths.txt')
        genelist_path =os.path.join(output_dir,'genelist.txt')
        output_sif = codecs.open(sif_path, 'w', 'utf-8')
        output_geneRole = collections.defaultdict(list)
        #occurence_dict = self.get_node_occurence(network_matrix)
        set_of_vlb = set()
        set_of_elb = set()
        for i in range(network_matrix.shape[0]):
            node1 = network_matrix.loc[i, 'node1']
            node2 = network_matrix.loc[i, 'node2']
            if (network_matrix.loc[i, 'is_ct_edge']):
                interact = 'cross-talk'
            else:
                interact = 'intra-talk'
            edge_role = network_matrix.loc[i, 'edge_role']
            if (node1 not in set_of_vlb):
                output_geneRole['geneLabel'].append(node1)
                output_geneRole['geneRealName'].append(node1.split('__')[0].upper())
                output_geneRole['cellType'].append(node1.split('__')[1])
                #output_geneRole['occurrence'].append(occurence_dict[node1])
                if (edge_role == 'start'):
                    output_geneRole['Role'].append('internal_gene')
                elif(edge_role == 'frequent pathway'):
                    output_geneRole['Role'].append('external_gene')
                else:
                    output_geneRole['Role'].append('intermediate_gene')
                set_of_vlb.add(node1)
            if (node2 not in set_of_vlb):
                output_geneRole['geneLabel'].append(node2)
                output_geneRole['geneRealName'].append(node2.split('__')[0].upper())
                output_geneRole['cellType'].append(node2.split('__')[1])
                #output_geneRole['occurrence'].append(occurence_dict[node2])
                if (edge_role == 'end' or edge_role == 'frequent pathway'):
                    output_geneRole['Role'].append('external_gene')
                else:
                    output_geneRole['Role'].append('intermediate_gene')
                set_of_vlb.add(node2)
            if ((node1, node2) not in set_of_elb):
                set_of_elb.add((node1, node2))
                set_of_elb.add((node2, node1))
                output_sif.write('{}\t{}\t{}\n'.format(node1, interact, node2))
        output_sif.close()
        generole_matrix = pd.DataFrame(output_geneRole)
        generole_matrix.to_csv(generole_path, sep='\t', index=False)
        network_matrix.to_csv(matrix_path, sep='\t', index=False)
        genelist = generole_matrix['geneRealName']
        genelist.to_csv(genelist_path,sep = ' ',index = False,header = False)
        return

    def output_network_sif(self, network_matrix, outputpath='./result/network.sif'):
        '''
        output network in a sif form for cytoscape
        :param network_matrix:
        :param outputpath:
        :return:
        '''
        output = codecs.open(outputpath, 'w', 'utf-8')
        for j in range(network_matrix.shape[0]):
            node1 = network_matrix.loc[j, 'node1']
            node2 = network_matrix.loc[j, 'node2']
            if (network_matrix.loc[j, 'is_ct_edge']):
                interact = 'cross-talk'
            else:
                interact = 'intra-talk'
            output.write('{}\t{}\t{}\n'.format(node1, interact, node2))
        output.close()
        return

    def get_node_occurence(self, network_matrix):
        """
        get node's occurence in a frequent pattern from different pseudo-patients
        :param network_matrix:
        :return:
        """
        occurrence_dict = dict()
        for i in range(network_matrix.shape[0]):
            node1 = network_matrix.loc[i, 'node1']
            node2 = network_matrix.loc[i, 'node2']
            if not occurrence_dict.__contains__(node1):
                occurrence_dict[node1] = 1
            else:
                occurrence_dict[node1] += 1
            if not occurrence_dict.__contains__(node2):
                occurrence_dict[node2] = 1
            else:
                occurrence_dict[node2] += 1
        return occurrence_dict

    def combine_FP_pathway(self, k, patients_path, association_test_ret, output_dir='./result'):
        """
        combine all the frequent pathways from each pseudo-patient to form a large FP
        :param k:
        :param patients_path:
        :param association_test_ret:
        :param output_dir:
        :return:
        """
        patients_list = os.listdir(patients_path)
        tested_FP_list = association_test_ret['idx of passed FP']
        combined_shortest_network = pd.DataFrame()
        for i in range(k):
            for patient in patients_list:
                patient_path = os.path.join(patients_path, patient)
                FP_path = os.path.join(patient_path, 'Frequent_pattern_' + str(tested_FP_list[i]))
                if (os.path.exists(FP_path)):
                    shortest_network = pd.read_table(os.path.join(FP_path, 'shortest_paths.txt'), sep='\t')
                    combined_shortest_network = pd.concat((combined_shortest_network, shortest_network))
            combined_shortest_network = combined_shortest_network.reset_index(drop=True)
            self.output_shortest_network_info(combined_shortest_network,
                                              os.path.join(output_dir, 'combined_FrequentPatterns',
                                                           'Frequent_pattern_' + str(
                                                               tested_FP_list[i])))
        return



    def find_represent_patient(self,k,driver):
        """
        select the patients with the most top k frequent subgraph as represent
        :param k: top k frequent subgraph
        :return:
        """
        flag = False
        for i in range(len(self.association_test_ret)):
                if driver == self.association_test_ret[i]['internal']:
                    association_test_ret_driver = self.association_test_ret[i]
                    flag = True
                    break
        assert flag == True , "association test not contation input driver/tumor subtype,please check again!"

        internal_vec = association_test_ret_driver['internal vec']
        patient_list = list(internal_vec[internal_vec==1].index)
        association_test_ret_driver_ext_mat = association_test_ret_driver['external matrix'].loc[patient_list,]
        if k > association_test_ret_driver_ext_mat.shape[1]:
            k = association_test_ret_driver_ext_mat.shape[1]
        print(np.sum(association_test_ret_driver_ext_mat.iloc[:, 0:k], axis=1))
        return patient_list[np.argmax(np.sum(association_test_ret_driver_ext_mat.iloc[:, 0:k], axis=1))]

